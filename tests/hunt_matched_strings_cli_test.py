"""Command-tree coverage for the matched-strings block (Style 1 — SDK-boundary mocks).

`hunt_matched_strings_test.py` drives the formatter directly and covers *which line a
given field value produces*, including the `output.extend` call inside `live_result` --
it invokes that method, so a deletion there does fail it. What it cannot observe is
everything ABOVE the formatter: that `live result` parses its argument, calls the SDK,
and hands the result to `output.live_result` rather than some other renderer.
`specs/04-testing.md` §Style 3 requires exactly this counterpart -- a command whose
rendering is covered that way "still needs at least one `CliRunner` test proving the
command reaches the formatter".

Measured, not assumed: rewiring the command to `output.live_feed([...])` leaves all 36
assertions in the sibling module passing and fails this module. The cassette tests cannot
catch it either -- they predate the field, so every result they render takes the silent
`None` branch.
"""
from unittest import TestCase, mock

from click.testing import CliRunner
from polyswarm_api import resources

from polyswarm.client import polyswarm as client

_API_KEY = '1' * 32
_API_URL = 'http://artifact-index-e2e:9696/v3'
_COMMUNITY = 'gamma'

_CONTENT = {
    'id': 123,
    'instance_id': 2,
    'livescan_id': 3,
    'created': '2022-05-26T19:41:33.797898',
    'sha256': 'f' * 64,
    'rule_name': 'dos_stub_message',
    'tags': '{pe,stub}',
    'polyscore': 0.5,
    'malware_family': None,
    'detections': {'malicious': 1, 'total': 1},
}

_STRINGS = [
    {'offset': 78, 'identifier': '$stub', 'length': 14,
     'data': '54 68 69 73 20 70 72 6F 67 72 61 6D 20 63', 'truncated': False},
]


def _live_result(**overrides):
    """A real `LiveHuntResult`, not a mock — the formatter reads polyscore, detections and
    the rest of the row, so a bare stub dies before it reaches the block under test. The
    floor (`polyswarm_api>=4.4.0`) guarantees this parses both matched-strings keys."""
    return resources.LiveHuntResult(dict(_CONTENT, **overrides))


class HuntMatchedStringsCliTest(TestCase):
    def setUp(self):
        self.cli = CliRunner()

    def _run(self, *cmd):
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY] + list(cmd),
            catch_exceptions=False,
        )

    def _live_result_output(self, **overrides):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.live_result',
                        return_value=_live_result(**overrides)):
            return self._run('--output-format', 'text', 'live', 'result', '123').output

    def test_live_result_renders_the_block_through_the_command_tree(self):
        output = self._live_result_output(matched_strings=_STRINGS)
        assert 'Matched Strings:' in output
        assert '$stub @ 0x4e' in output

    def test_live_result_reports_a_withheld_count_through_the_command_tree(self):
        output = self._live_result_output(matched_strings=_STRINGS,
                                          matched_strings_dropped=19)
        assert '19 more not shown' in output

    def test_live_result_stays_silent_when_nothing_was_reported(self):
        # No matched_strings key at all -- what a detail route serves for a result that
        # predates the feature, and what every list route serves always.
        assert 'Matched Strings' not in self._live_result_output()
