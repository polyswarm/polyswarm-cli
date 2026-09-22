"""IoC refanging through the CLI.

Threat-intel reports print indicators defanged (``hxxps[:]//evil[.]com``,
``127[.]0[.]0[.]1``). The SDK refangs URL / domain / IP inputs before building
a request (``polyswarm_api.refang``); these tests pin that every CLI entry point
that takes such an input reaches the wire refanged, that ``--no-refang`` sends
it verbatim, and that live input is unchanged.

The SDK is mocked at its transport: ``PolyswarmSession.execute``, the
documented session customization point, receives the fully built
``PolyswarmRequest`` descriptor, and the tests read its ``params`` /
``input_json`` directly. Mocking any higher — at ``search_url`` and friends —
would prove nothing, because the refang runs INSIDE those endpoint methods.
"""
from unittest import TestCase, mock

from click.testing import CliRunner

from polyswarm.client import polyswarm as client


_API_KEY = '1' * 32
_API_URL = 'http://artifact-index-e2e:9696/v3'
_COMMUNITY = 'gamma'


class _Stop(Exception):
    """Stops the command at its first request, which is the one carrying the IoC."""


def _params(request):
    params = request.params
    if isinstance(params, dict):
        pairs = []
        for key, value in params.items():
            if isinstance(value, (list, tuple)):
                pairs.extend((key, v) for v in value)
            else:
                pairs.append((key, value))
        return pairs
    return list(params)


class RefangCliTest(TestCase):
    def setUp(self):
        self.cli = CliRunner()
        self.requests = []

        def fake_execute(session, request):
            self.requests.append(request)
            raise _Stop()

        patcher = mock.patch('polyswarm_api.session.PolyswarmSession.execute',
                             autospec=True, side_effect=fake_execute)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _run(self, *cmd, refang=True):
        flags = [] if refang else ['--no-refang']
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY] + flags + list(cmd),
        )

    def _first_params(self):
        self.assertTrue(self.requests, 'no request reached the SDK')
        return _params(self.requests[0])

    def _first_body(self):
        self.assertTrue(self.requests, 'no request reached the SDK')
        return self.requests[0].input_json

    # ── search ────────────────────────────────────────────────────────────

    def test_search_url_refangs(self):
        self._run('search', 'url', 'hxxps[:]//evil[.]com/x')
        self.assertIn(('url', 'https://evil.com/x'), self._first_params())

    def test_search_url_no_refang_sends_raw(self):
        self._run('search', 'url', 'hxxps[:]//evil[.]com/x', refang=False)
        self.assertIn(('url', 'hxxps[:]//evil[.]com/x'), self._first_params())

    def test_search_url_live_value_is_unchanged(self):
        self._run('search', 'url', 'https://example.com/a[.]b')
        self.assertIn(('url', 'https://example.com/a[.]b'), self._first_params())

    def test_search_metadata_refangs_ioc_options_but_not_the_query(self):
        self._run('search', 'metadata', '-p', '127[.]0[.]0[.]1', '-u', 'hxxp://evil[.]com',
                  '-d', 'evil[dot]com', 'strings.domains:"bad[.]org"')
        params = self._first_params()
        self.assertIn(('ips', '127.0.0.1'), params)
        self.assertIn(('urls', 'http://evil.com'), params)
        self.assertIn(('domains', 'evil.com'), params)
        self.assertIn(('query', 'strings.domains:"bad[.]org"'), params)

    def test_search_metadata_no_refang_sends_raw(self):
        self._run('search', 'metadata', '-p', '127[.]0[.]0[.]1', 'x:*', refang=False)
        self.assertIn(('ips', '127[.]0[.]0[.]1'), self._first_params())

    def test_search_ioc_ip_refangs(self):
        self._run('search', 'ioc', 'ip', '10[.]0[.]0[.]1')
        self.assertIn(('ip', '10.0.0.1'), self._first_params())

    def test_search_ioc_domain_refangs(self):
        self._run('search', 'ioc', 'domain', 'evil(.)com')
        self.assertIn(('domain', 'evil.com'), self._first_params())

    def test_search_ioc_no_refang_sends_raw(self):
        self._run('search', 'ioc', 'domain', 'evil(.)com', refang=False)
        self.assertIn(('domain', 'evil(.)com'), self._first_params())

    def test_search_known_refangs(self):
        self._run('search', 'known', '-p', '8[.]8[.]8[.]8', '-d', 'good[.]example')
        params = self._first_params()
        self.assertIn(('ip', '8.8.8.8'), params)
        self.assertIn(('domain', 'good.example'), params)

    # ── scan / sandbox / analyze-ip (submissions) ─────────────────────────

    def test_scan_url_accepts_and_refangs_a_defanged_url(self):
        # The command validates URLs before submitting; a defanged URL must
        # be validated in its refanged form, not rejected.
        result = self._run('scan', 'url', '--nowait', 'hxxps[:]//evil[.]com/x')
        self.assertNotIn('is not valid', result.output)
        self.assertEqual(self._first_body()['artifact_name'], 'https://evil.com/x')

    def test_scan_url_file_lines_are_refanged(self):
        with self.cli.isolated_filesystem():
            with open('urls.txt', 'w') as f:
                f.write('hxxp://evil[.]com/a\n')
            self._run('scan', 'url', '--nowait', '-r', 'urls.txt')
        self.assertEqual(self._first_body()['artifact_name'], 'http://evil.com/a')

    def test_scan_url_no_refang_keeps_rejecting_a_defanged_url(self):
        result = self._run('scan', 'url', '--nowait', 'hxxps[:]//evil[.]com/x', refang=False)
        self.assertIn('is not valid', result.output)
        self.assertEqual(self.requests, [])

    def test_sandbox_url_accepts_and_refangs_a_defanged_url(self):
        result = self._run('sandbox', 'url', 'provider', 'hxxps[:]//evil[.]com/x', '--vm_slug', 'vm')
        self.assertNotIn('is not valid', result.output)
        self.assertEqual(self._first_body()['artifact_name'], 'https://evil.com/x')

    def test_sandbox_url_no_refang_keeps_rejecting_a_defanged_url(self):
        result = self._run('sandbox', 'url', 'provider', 'hxxps[:]//evil[.]com/x', '--vm_slug', 'vm',
                           refang=False)
        self.assertIn('is not valid', result.output)
        self.assertEqual(self.requests, [])

    # ── QR-code submissions: the argument is an image path, never refanged ──
    #
    # The exemption lives in the SDK: a ``preprocessing={'type': 'qrcode'}``
    # submission skips refanging entirely. ``qr[.]png`` would otherwise pass
    # the gate (``png`` has the shape of a TLD) and be rewritten to
    # ``qr.png``, a path that does not exist.

    def test_scan_url_qrcode_file_path_is_not_refanged(self):
        with self.cli.isolated_filesystem():
            with open('qr[.]png', 'wb') as f:
                f.write(b'not really a png')
            result = self._run('scan', 'url', '--nowait', '--qrcode-file', 'qr[.]png')
        self.assertNotIsInstance(result.exception, TypeError)
        self.assertEqual(self._first_body()['artifact_name'], 'qr[.]png')

    def test_sandbox_url_qrcode_file_submits_with_no_url(self):
        # The qrcode branch hands the SDK ``url=None``; refanging must let it
        # through untouched rather than fail on a non-string.
        with self.cli.isolated_filesystem():
            with open('qr[.]png', 'wb') as f:
                f.write(b'not really a png')
            result = self._run('sandbox', 'url', 'provider', '--qrcode-file', 'qr[.]png', '--vm_slug', 'vm')
        self.assertNotIsInstance(result.exception, TypeError)
        self.assertEqual(self._first_body()['artifact_name'], 'qr[.]png')

    # ── known-host catalogue writes ───────────────────────────────────────

    def test_known_add_refangs_the_host(self):
        self._run('known', 'add', 'domain', 'good[.]example', 'feed')
        self.assertEqual(self._first_body()['host'], 'good.example')

    def test_known_add_no_refang_sends_raw(self):
        self._run('known', 'add', 'domain', 'good[.]example', 'feed', refang=False)
        self.assertEqual(self._first_body()['host'], 'good[.]example')

    def test_known_update_refangs_the_host(self):
        self._run('known', 'update', '7', 'domain', 'good[.]example', 'feed', '-g', 'true')
        self.assertEqual(self._first_body()['host'], 'good.example')

    def test_known_update_no_refang_sends_raw(self):
        self._run('known', 'update', '7', 'domain', 'good[.]example', 'feed', '-g', 'true', refang=False)
        self.assertEqual(self._first_body()['host'], 'good[.]example')

    def test_metadata_analyze_ip_refangs(self):
        # CLI-owned request (it bypasses the SDK endpoint methods), so the CLI
        # applies the SDK's refang itself.
        self._run('metadata', 'analyze-ip', '192(.)168(.)100(.)200')
        self.assertEqual(self._first_body(), {'url': '192.168.100.200'})

    def test_metadata_analyze_ip_no_refang_sends_raw(self):
        self._run('metadata', 'analyze-ip', '192(.)168(.)100(.)200', refang=False)
        self.assertEqual(self._first_body(), {'url': '192(.)168(.)100(.)200'})

    # ── the flag itself ───────────────────────────────────────────────────

    def test_no_refang_flag_is_documented_in_help(self):
        result = self.cli.invoke(client.polyswarm_cli, ['--help'])
        self.assertIn('--no-refang', result.output)
