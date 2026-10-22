"""``historical start --window-days`` and the ``Time Range`` line of the hunt text block.

The command is driven through autospec'd SDK-boundary mocks (specs/04-testing.md, Style 1),
so every call is also a signature check against the installed SDK: one without
``window_days`` fails at the mock. The line itself is a Style 3 formatter test on real SDK
resources built from dicts.
"""
import json
from pathlib import Path
from unittest import TestCase, mock

from click.testing import CliRunner

from polyswarm.client import polyswarm as client
from polyswarm.formatters import text
from polyswarm_api import resources

_RULE_FILE = Path(__file__).resolve().parent / 'eicar.yara'
_GLOBALS = ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma']


def _hunt(**overrides):
    content = dict(id='9', status='PENDING', progress=0.0, active=None,
                   created='2026-10-01T12:00:00+00:00', summary=None,
                   results_csv_uri=None, ruleset_name='n', yara=None)
    content.update(overrides)
    return resources.HistoricalHunt(content, api=None)


def _echo_window(_api, _rule, **kwargs):
    """Stand-in for the server: the created hunt carries the window it was asked for."""
    return _hunt(window_days=kwargs.get('window_days'))


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
                result, historical_create = self._start(str(_RULE_FILE), '--window-days', str(days))
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
        result, historical_create = self._start(str(_RULE_FILE), '--window-days', '45')
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
        assert '--window-days [30|60|90|180]' in helptext, helptext
        assert 'Defaults to max' in helptext, helptext


class HuntTimeRangeFormatterTest(TestCase):
    def _lines(self, hunt, method='hunt'):
        return getattr(text.TextOutput(color=False), method)(hunt, write=False)

    def test_a_window_renders_as_the_last_n_days(self):
        assert 'Time Range: Last 30 days' in self._lines(_hunt(window_days=30))

    def test_no_window_renders_as_the_platform_maximum(self):
        # An explicit null and a key the server never sent mean the same thing.
        for hunt in (_hunt(window_days=None), _hunt()):
            lines = self._lines(hunt)
            assert 'Time Range: Platform maximum' in lines
            assert not [line for line in lines if line.startswith('Time Range: Last')]

    def test_the_line_follows_created_at(self):
        lines = self._lines(_hunt(window_days=90))
        created = next(i for i, line in enumerate(lines) if line.startswith('Created at:'))
        assert lines[created + 1] == 'Time Range: Last 90 days'

    def test_a_deleted_hunt_shows_it_too(self):
        # hunt_deletion embeds the hunt block.
        assert 'Time Range: Last 60 days' in self._lines(_hunt(window_days=60), 'hunt_deletion')


class HistoricalStartRendersTimeRangeTest(TestCase):
    """The command reaches the formatter: what the user asked for is what the hunt shows."""

    def _start(self, *args, fmt='text', **patch):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.historical_create',
                        autospec=True, **patch):
            return CliRunner().invoke(
                client.polyswarm_cli,
                _GLOBALS + ['--output-format', fmt, 'historical', 'start', '-r', '5', *args],
                catch_exceptions=False)

    def test_the_started_hunt_shows_the_window_it_was_started_with(self):
        result = self._start('--window-days', '60', side_effect=_echo_window)
        assert result.exit_code == 0, result.output
        assert 'Time Range: Last 60 days' in result.output

    def test_a_start_without_the_flag_shows_the_platform_maximum(self):
        result = self._start(side_effect=_echo_window)
        assert result.exit_code == 0, result.output
        assert 'Time Range: Platform maximum' in result.output

    def test_json_carries_the_raw_key_and_no_label(self):
        # The JSON formatter dumps the resource's own JSON, so it needed no change.
        result = self._start(fmt='json', return_value=_hunt(window_days=30))
        assert result.exit_code == 0, result.output
        assert json.loads(result.output)['window_days'] == 30
        assert 'Time Range' not in result.output
