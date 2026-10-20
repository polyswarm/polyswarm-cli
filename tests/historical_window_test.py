"""``historical start --window-days``: what reaches ``historical_create``.

autospec'd SDK-boundary mocks (specs/04-testing.md, Style 1), so every call is also a
signature check against the installed SDK: one without ``window_days`` fails at the mock.
"""
from pathlib import Path
from unittest import TestCase, mock

from click.testing import CliRunner

from polyswarm.client import polyswarm as client
from polyswarm_api import resources

_RULE_FILE = Path(__file__).resolve().parent / 'eicar.yara'
_GLOBALS = ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma']


def _hunt(**overrides):
    content = dict(id='9', status='PENDING', progress=0.0, active=None,
                   created='2026-10-01T12:00:00+00:00', summary=None,
                   results_csv_uri=None, ruleset_name='n', yara=None)
    content.update(overrides)
    return resources.HistoricalHunt(content, api=None)


class HistoricalStartWindowTest(TestCase):
    def _start(self, *args):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.historical_create',
                        autospec=True, return_value=_hunt()) as historical_create:
            result = CliRunner().invoke(
                client.polyswarm_cli, _GLOBALS + ['historical', 'start', *args],
                catch_exceptions=False)
        return result, historical_create

    def test_each_window_is_forwarded_as_an_int(self):
        for days in (30, 60, 90, 180):
            with self.subTest(days=days):
                result, historical_create = self._start(str(_RULE_FILE), '-w', str(days))
                assert result.exit_code == 0, result.output
                historical_create.assert_called_once_with(
                    mock.ANY, _RULE_FILE.read_text(), ruleset_name='eicar.yara',
                    window_days=days)
                # 30 == '30' is False, but only the type says it is not a float or a bool.
                assert type(historical_create.call_args.kwargs['window_days']) is int

    def test_no_flag_forwards_no_window_at_all(self):
        # A script written before the flag keeps making the SDK call it always made.
        result, historical_create = self._start(str(_RULE_FILE))
        assert result.exit_code == 0, result.output
        historical_create.assert_called_once_with(
            mock.ANY, _RULE_FILE.read_text(), ruleset_name='eicar.yara')
        assert 'window_days' not in historical_create.call_args.kwargs

    def test_window_composes_with_a_stored_rule(self):
        result, historical_create = self._start('--rule-id', '5', '--window-days', '90')
        assert result.exit_code == 0, result.output
        historical_create.assert_called_once_with(mock.ANY, 5, window_days=90)

    def test_a_window_outside_the_choices_is_a_usage_error(self):
        result, historical_create = self._start(str(_RULE_FILE), '-w', '45')
        assert result.exit_code == 2, result.output
        # Names the refused value and what is allowed; click's wording varies by version.
        for text in ('45', '30', '60', '90', '180'):
            assert text in result.output, result.output
        historical_create.assert_not_called()

    def test_help_documents_the_choices_and_the_default(self):
        result = CliRunner().invoke(
            client.polyswarm_cli, _GLOBALS + ['historical', 'start', '--help'],
            catch_exceptions=False)
        assert result.exit_code == 0, result.output
        helptext = ' '.join(result.output.split())
        assert '-w, --window-days [30|60|90|180]' in helptext, helptext
        assert 'platform maximum' in helptext, helptext
