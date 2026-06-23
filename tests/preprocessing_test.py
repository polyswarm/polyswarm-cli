"""Tests for the file-preprocessing options on `scan file` and `sandbox file`.

These mock at the SDK boundary (the `Polyswarm` wrapper's `scan_file`, and the
inherited `PolyswarmAPI.sandbox_file`) and assert the CLI threads the right
`preprocessing` dict through to the SDK. JSON output is used so the fake return
values render through `_to_json(result.json)` without needing a full resource.

Covers the new `--is-pdf` / `--pdf-password` branch and the updated
mutual-exclusivity guard on `scan file`.
"""
from unittest import TestCase, mock
from unittest.mock import MagicMock

from click.testing import CliRunner

from polyswarm.client import polyswarm as client


_API_KEY = '1' * 32
_API_URL = 'http://artifact-index-e2e:9696/v3'
_COMMUNITY = 'gamma'


def _fake_result():
    obj = MagicMock()
    obj.json = {'id': '1', 'result': 'ok'}
    return obj


class PreprocessingCliTest(TestCase):
    def setUp(self):
        self.cli = CliRunner()

    def _run(self, *cmd):
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY, '--fmt', 'json'] + list(cmd),
        )

    # --- scan file --------------------------------------------------------

    def test_scan_file_is_pdf(self):
        with mock.patch('polyswarm.polyswarm.Polyswarm.scan_file',
                        return_value=iter([_fake_result()])) as m:
            with self.cli.isolated_filesystem():
                with open('sample.pdf', 'w') as fh:
                    fh.write('x')
                result = self._run('scan', 'file', '--is-pdf', 'sample.pdf')
        assert result.exit_code == 0, result.output
        # scan_file(path, recursive, timeout, nowait, scan_config, preprocessing, expiration_window)
        preprocessing = m.call_args.args[5]
        assert preprocessing == {'type': 'pdf'}

    def test_scan_file_pdf_password(self):
        with mock.patch('polyswarm.polyswarm.Polyswarm.scan_file',
                        return_value=iter([_fake_result()])) as m:
            with self.cli.isolated_filesystem():
                with open('sample.pdf', 'w') as fh:
                    fh.write('x')
                result = self._run('scan', 'file', '--pdf-password', 's3cret', 'sample.pdf')
        assert result.exit_code == 0, result.output
        preprocessing = m.call_args.args[5]
        assert preprocessing == {'type': 'pdf', 'password': 's3cret'}

    def test_scan_file_pdf_and_zip_mutually_exclusive(self):
        with mock.patch('polyswarm.polyswarm.Polyswarm.scan_file') as m:
            with self.cli.isolated_filesystem():
                with open('sample.pdf', 'w') as fh:
                    fh.write('x')
                result = self._run('scan', 'file', '--is-pdf', '--is-zip', 'sample.pdf')
        assert result.exit_code != 0
        m.assert_not_called()
        # The guard's message must mention the pdf flags now that they count.
        message = result.output + (str(result.exception) if result.exception else '')
        assert '--is-pdf/--pdf-password' in message

    # --- sandbox file -----------------------------------------------------

    def test_sandbox_file_is_pdf(self):
        with mock.patch('polyswarm.polyswarm.Polyswarm.sandbox_file',
                        return_value=_fake_result()) as m:
            with self.cli.isolated_filesystem():
                with open('sample.pdf', 'w') as fh:
                    fh.write('x')
                result = self._run('sandbox', 'file', 'cape', 'sample.pdf', '--is-pdf')
        assert result.exit_code == 0, result.output
        assert m.call_args.kwargs['preprocessing'] == {'type': 'pdf'}

    def test_sandbox_file_pdf_password(self):
        with mock.patch('polyswarm.polyswarm.Polyswarm.sandbox_file',
                        return_value=_fake_result()) as m:
            with self.cli.isolated_filesystem():
                with open('sample.pdf', 'w') as fh:
                    fh.write('x')
                result = self._run('sandbox', 'file', 'cape', 'sample.pdf', '--pdf-password', 's3cret')
        assert result.exit_code == 0, result.output
        assert m.call_args.kwargs['preprocessing'] == {'type': 'pdf', 'password': 's3cret'}

    def test_sandbox_file_pdf_and_zip_mutually_exclusive(self):
        with mock.patch('polyswarm.polyswarm.Polyswarm.sandbox_file') as m:
            with self.cli.isolated_filesystem():
                with open('sample.pdf', 'w') as fh:
                    fh.write('x')
                result = self._run('sandbox', 'file', 'cape', 'sample.pdf', '--is-pdf', '--is-zip')
        assert result.exit_code != 0
        m.assert_not_called()
        message = result.output + (str(result.exception) if result.exception else '')
        assert '--is-pdf/--pdf-password' in message
