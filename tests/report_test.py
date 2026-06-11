"""Tests for the report CLI commands.

These tests mock the SDK methods directly to keep the test runtime
self-contained (no live artifact-index, no VCR cassettes).
"""
from unittest import TestCase, mock
from unittest.mock import MagicMock

from click.testing import CliRunner
from polyswarm_api import settings

from polyswarm.client import polyswarm as client


_API_KEY = '1' * 32
_API_URL = 'http://artifact-index-e2e:9696/v3'
_COMMUNITY = 'gamma'


def _fake_report_task(id_=123):
    obj = MagicMock()
    obj.id = id_
    obj.json = {'id': id_, 'state': 'SUCCEEDED'}
    return obj


def _fake_local_artifact(name='report.pdf', path='/tmp/report.pdf'):
    obj = MagicMock()
    obj.artifact_name = name
    obj.name = path
    return obj


class ReportCreateCliTest(TestCase):
    def setUp(self):
        self.cli = CliRunner()

    def _run(self, *cmd):
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY,
             '--output-format', 'json'] + list(cmd),
            catch_exceptions=False,
        )

    def test_report_create_waits_and_downloads(self):
        """The non---nowait path: create, wait, then download via report_download."""
        with mock.patch('polyswarm_api.api.PolyswarmAPI.report_create',
                        return_value=_fake_report_task()) as m_create, \
             mock.patch('polyswarm_api.api.PolyswarmAPI.report_wait_for',
                        return_value=_fake_report_task()) as m_wait, \
             mock.patch('polyswarm_api.api.PolyswarmAPI.report_download',
                        return_value=_fake_local_artifact()) as m_download:
            result = self._run('report', 'create', 'pdf', 'scan', '12345')
        assert result.exit_code == 0, result.output
        m_create.assert_called_once_with(type='scan',
                                         format='pdf',
                                         template_id=None,
                                         template_metadata=None,
                                         instance_id='12345')
        m_wait.assert_called_once_with(123, settings.DEFAULT_REPORT_TIMEOUT)
        m_download.assert_called_once_with(123, mock.ANY)
        assert 'report.pdf' in result.output

    def test_report_create_nowait_skips_download(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.report_create',
                        return_value=_fake_report_task()) as m_create, \
             mock.patch('polyswarm_api.api.PolyswarmAPI.report_download') as m_download:
            result = self._run('report', 'create', 'pdf', 'scan', '12345', '--nowait')
        assert result.exit_code == 0, result.output
        m_create.assert_called_once()
        m_download.assert_not_called()
