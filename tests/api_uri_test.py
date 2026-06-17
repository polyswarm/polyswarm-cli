"""Tests for the --api-uri endpoint resolution and the convenience
environment shortcuts (--stage / --local / --prod-eu / --stage-eu).

The resolver is unit-tested directly; the CLI integration tests mock the SDK
boundary and assert the resolved endpoint reaches the client.
"""
from unittest import TestCase, mock
from unittest.mock import MagicMock

import click
from click.testing import CliRunner

from polyswarm.client import polyswarm as client
from polyswarm.client.polyswarm import resolve_api_uri, PROD_API_URI, API_URI_SHORTCUTS


_API_KEY = '1' * 32


def _shortcuts(stage=False, local=False, prod_eu=False, stage_eu=False):
    return {'stage': stage, 'local': local, 'prod_eu': prod_eu, 'stage_eu': stage_eu}


class ResolveApiUriTest(TestCase):
    def test_default_is_production(self):
        assert resolve_api_uri(None, _shortcuts()) == PROD_API_URI
        assert PROD_API_URI == 'https://api.polyswarm.network/v3'

    def test_explicit_api_uri_passthrough(self):
        assert resolve_api_uri('http://example.test/v3', _shortcuts()) == 'http://example.test/v3'

    def test_each_shortcut_resolves(self):
        expected = {
            'stage': 'https://api.stage-v3.polyswarm.network/v3',
            'local': 'http://localhost:9696/v3',
            'prod_eu': 'https://api.prod-eu-v3.polyswarm.network/v3',
            'stage_eu': 'https://api.stage-eu-v3.polyswarm.network/v3',
        }
        # guard against the constant drifting from the verified ingress hosts
        assert API_URI_SHORTCUTS == expected
        for name, url in expected.items():
            assert resolve_api_uri(None, _shortcuts(**{name: True})) == url, name

    def test_two_shortcuts_are_mutually_exclusive(self):
        with self.assertRaises(click.UsageError):
            resolve_api_uri(None, _shortcuts(stage=True, local=True))

    def test_shortcut_conflicts_with_explicit_api_uri(self):
        with self.assertRaises(click.UsageError):
            resolve_api_uri('http://example.test/v3', _shortcuts(stage=True))


class ApiUriCliTest(TestCase):
    def setUp(self):
        self.cli = CliRunner()

    def _resolved_base(self, *global_opts):
        """Invoke `metadata analyze-ip` (which builds `{uri}/instance/url` via
        the real Polyswarm.submit_url) with the SDK's _single mocked, and return
        the base endpoint the client actually used."""
        fake = MagicMock()
        fake.json = {'id': 1}
        with mock.patch('polyswarm_api.api.PolyswarmAPI._single', return_value=fake) as m:
            result = self.cli.invoke(
                client.polyswarm_cli,
                ['-a', _API_KEY, *global_opts, '--output-format', 'json',
                 'metadata', 'analyze-ip', '1.2.3.4'],
                catch_exceptions=False,
            )
        assert result.exit_code == 0, result.output
        url = m.call_args.args[0]['url']
        assert url.endswith('/instance/url'), url
        return url[:-len('/instance/url')]

    def test_default_targets_production(self):
        assert self._resolved_base() == 'https://api.polyswarm.network/v3'

    def test_stage_shortcut(self):
        assert self._resolved_base('--stage') == 'https://api.stage-v3.polyswarm.network/v3'

    def test_local_shortcut(self):
        assert self._resolved_base('--local') == 'http://localhost:9696/v3'

    def test_prod_eu_shortcut(self):
        assert self._resolved_base('--prod-eu') == 'https://api.prod-eu-v3.polyswarm.network/v3'

    def test_stage_eu_shortcut(self):
        assert self._resolved_base('--stage-eu') == 'https://api.stage-eu-v3.polyswarm.network/v3'

    def test_explicit_api_uri_still_works(self):
        assert self._resolved_base('--api-uri', 'http://example.test/v3') == 'http://example.test/v3'

    def test_shortcut_with_api_uri_errors(self):
        result = self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '--stage', '--api-uri', 'http://example.test/v3',
             'metadata', 'analyze-ip', '1.2.3.4'],
        )
        assert result.exit_code == 2
        assert 'api-uri' in result.output

    def test_two_shortcuts_error(self):
        result = self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '--stage', '--stage-eu', 'metadata', 'analyze-ip', '1.2.3.4'],
        )
        assert result.exit_code == 2
        assert 'mutually exclusive' in result.output
