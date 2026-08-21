"""Pure-unit rendering tests for matched strings on hunt results.

No CliRunner / VCR — these drive the text formatter directly with constructed SDK
resources (specs/04-testing.md, Style 3), because the point is which line a given
field value produces, not command-tree behaviour.

The contract under test is three-state (specs/05-downstream-contract.md in the SDK):
`None` is "not reported", `[]` is "matched with no byte evidence", `[...]` is the
evidence. All three must produce a DIFFERENT, self-explaining line — the feature
exists to answer "why did this rule hit", and rendering `None` as silence answers
nothing while looking identical to a rule that had nothing to show.
"""
import click
import pytest
from polyswarm_api import resources

from polyswarm.formatters.text import TextOutput

_COMMON = {
    'id': 123,
    'instance_id': 2,
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
    {'offset': 0, 'identifier': '$mz', 'length': 512,
     'data': '4D 5A 90 00 ...', 'truncated': True},
]

# (resource class, formatter method name)
PATHS = [
    (resources.LiveHuntResult, 'live_result'),
    (resources.HistoricalHuntResult, 'historical_result'),
]


def _render(cls, method, **extra):
    content = dict(_COMMON, **extra)
    content['livescan_id' if cls is resources.LiveHuntResult else 'historicalscan_id'] = 3
    output = TextOutput(color=False)
    lines = getattr(output, method)(cls(content), write=False)
    return click.unstyle('\n'.join(lines))


def _matched_lines(text):
    """Just the matched-strings block: its header line plus the indented entries."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith('Matched Strings:'))
    end = start + 1
    while end < len(lines) and lines[end].startswith('  '):
        end += 1
    return lines[start:end]


@pytest.mark.parametrize('cls,method', PATHS)
def test_absent_names_its_causes(cls, method):
    """A silent omission is indistinguishable from a rule that had nothing to show, so
    the line must appear and must say WHY. It names causes rather than a command to run:
    this same method renders `live feed` rows and single-result fetches alike."""
    line, = _matched_lines(_render(cls, method))
    # Substrings, not the whole sentence: the line must keep saying "unavailable" and
    # must keep naming BOTH causes, but the prose around them is free to be reworded
    # without this test turning into a spelling check.
    assert 'unavailable' in line
    assert 'not recorded' in line   # the legacy-result / removed-data cause
    assert 'list view' in line      # the list-route cause


@pytest.mark.parametrize('cls,method', PATHS)
def test_explicit_null_renders_the_same_as_absent(cls, method):
    assert _matched_lines(_render(cls, method)) == \
        _matched_lines(_render(cls, method, matched_strings=None))


@pytest.mark.parametrize('cls,method', PATHS)
def test_empty_says_the_rule_matched_without_evidence(cls, method):
    """`[]` must NOT read as an error or as the absent case — the rule really did match."""
    line, = _matched_lines(_render(cls, method, matched_strings=[]))
    assert 'none' in line
    assert 'without byte evidence' in line
    assert 'unavailable' not in line


@pytest.mark.parametrize('cls,method', PATHS)
def test_empty_and_absent_are_distinguishable(cls, method):
    """The whole reason the server keeps them apart; collapsing them here wastes that."""
    assert _matched_lines(_render(cls, method)) != \
        _matched_lines(_render(cls, method, matched_strings=[])) 


@pytest.mark.parametrize('cls,method', PATHS)
def test_populated_renders_identifier_offset_length_and_data(cls, method):
    header, first, second = _matched_lines(_render(cls, method, matched_strings=_STRINGS))
    assert header == 'Matched Strings:'
    assert first == '  $stub @ 0x4e (14 bytes): 54 68 69 73 20 70 72 6F 67 72 61 6D 20 63'
    assert second == '  $mz @ 0x0 (512 bytes, truncated): 4D 5A 90 00 ...'


@pytest.mark.parametrize('cls,method', PATHS)
def test_truncation_is_marked_only_where_it_applies(cls, method):
    _, first, second = _matched_lines(_render(cls, method, matched_strings=_STRINGS))
    assert 'truncated' not in first
    assert 'truncated' in second


@pytest.mark.parametrize('cls,method', PATHS)
def test_block_sits_between_tags_and_download_url(cls, method):
    """Placement is the acceptance criteria — alongside Rule / Tags, not appended last."""
    text = _render(cls, method, matched_strings=_STRINGS, download_url='http://minio/x')
    lines = text.splitlines()
    tags = next(i for i, line in enumerate(lines) if line.startswith('Tags:'))
    matched = next(i for i, line in enumerate(lines) if line.startswith('Matched Strings:'))
    download = next(i for i, line in enumerate(lines) if line.startswith('Download Url:'))
    assert tags < matched < download
