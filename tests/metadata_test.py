"""Tests for the metadata CLI commands.

These tests mock the SDK methods directly to keep the test runtime
self-contained (no live artifact-index, no VCR cassettes).
"""
from unittest import TestCase, mock
from unittest.mock import MagicMock

from click.testing import CliRunner
from polyswarm_api import resources

from polyswarm.client import polyswarm as client


_API_KEY = '1' * 32
_API_URL = 'http://artifact-index-e2e:9696/v3'
_COMMUNITY = 'gamma'


def _fake_instance(url='https://example.com'):
    obj = MagicMock()
    obj.id = 456
    obj.json = {'id': 456, 'filename': url, 'type': 'URL'}
    return obj


class AnalyzeIpCliTest(TestCase):
    def setUp(self):
        self.cli = CliRunner()

    def _run(self, *cmd):
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY,
             '--output-format', 'json'] + list(cmd),
            catch_exceptions=False,
        )

    def test_analyze_ip_submits_url(self):
        """Exercises the real Polyswarm.submit_url body; mocks the SDK's _single
        execution helper (the documented boundary for CLI-owned inline endpoints,
        see specs/05-sdk-contract.md) and pins the request shape it builds."""
        with mock.patch('polyswarm_api.api.PolyswarmAPI._single',
                        return_value=_fake_instance()) as m:
            result = self._run('metadata', 'analyze-ip', 'https://example.com')
        assert result.exit_code == 0, result.output
        m.assert_called_once()
        request = m.call_args.args[0]
        assert request['method'] == 'POST'
        assert request['url'] == f'{_API_URL}/instance/url'
        assert request['params'] == {'community': _COMMUNITY}
        assert request['json'] == {'url': 'https://example.com'}
        assert m.call_args.kwargs['result_parser'] is resources.ArtifactInstance
        assert '"id": 456' in result.output

    def test_analyze_ip_multiple_urls(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI._single',
                        return_value=_fake_instance()) as m:
            result = self._run('metadata', 'analyze-ip', '1.2.3.4', '5.6.7.8')
        assert result.exit_code == 0, result.output
        assert m.call_count == 2
        submitted = [c.args[0]['json']['url'] for c in m.call_args_list]
        assert submitted == ['1.2.3.4', '5.6.7.8']
