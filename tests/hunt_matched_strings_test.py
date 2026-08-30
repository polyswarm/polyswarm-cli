"""Pure-unit rendering tests for matched strings on hunt results.

No CliRunner / VCR — these drive the text formatter directly with constructed SDK
resources (specs/04-testing.md, Style 3), because the point is which line a given
field value produces, not command-tree behaviour.

The contract under test is three-state (specs/05-downstream-contract.md in the SDK):
`None` is "not reported", `[]` is "matched with no byte evidence", `[...]` is the
evidence, and the three must stay distinguishable in the output.

`None` renders as silence on purpose: it is dominated by the list route, which can
never carry strings, so a per-row explanation there is a false alarm rather than
information. `[]` keeps its line — that one only ever reaches a detail route, where
"the rule matched with nothing to show" is a real answer to "why did this hit".
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
def _sdk_carries_the_fields():
    """Whether the installed SDK parses the attributes this module renders.

    The declared pin (`polyswarm_api>=4.3.0`) still admits SDKs predating them -- 4.3.0
    itself is released without them -- so `pip install .[tests] && pytest` against the
    floor would fail this module wholesale. CI resolves the paired SDK branch and runs it
    for real. Remove this guard when the floor is raised past the release that adds them
    (specs/05-sdk-contract.md, §Current floor).
    """
    probe = resources.LiveHuntResult(dict(_COMMON, livescan_id=3))
    return hasattr(probe, 'matched_strings') and hasattr(probe, 'matched_strings_dropped')


# Applied per-test, NOT as a module-level pytestmark. The two older-SDK tests below build
# a resource and pop the attribute off, so they pass on a floor SDK -- and that is the ONE
# install where they guard anything. A module-level skip took them out of exactly the
# configuration they model, leaving the getattr defence verified by nothing there.
needs_sdk_fields = pytest.mark.skipif(
    not _sdk_carries_the_fields(),
    reason='installed SDK predates matched_strings / matched_strings_dropped')


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
    """The matched-strings block -- header plus indented entries -- or [] if absent."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith('Matched Strings:')), None)
    if start is None:
        return []
    end = start + 1
    while end < len(lines) and lines[end].startswith('  '):
        end += 1
    return lines[start:end]


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_absent_renders_nothing(cls, method):
    """None is dominated by the list route, which can never carry strings -- `live feed`
    loops over this same method -- so an explanation there would be a permanent false
    alarm on every row. Silence, not a message."""
    assert _matched_lines(_render(cls, method)) == []
    assert 'Matched Strings' not in _render(cls, method)


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_explicit_null_renders_the_same_as_absent(cls, method):
    assert _matched_lines(_render(cls, method)) == \
        _matched_lines(_render(cls, method, matched_strings=None))


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_empty_says_the_rule_matched_without_evidence(cls, method):
    """`[]` must NOT read as an error or as the absent case — the rule really did match."""
    line, = _matched_lines(_render(cls, method, matched_strings=[]))
    assert 'none' in line
    assert 'without byte evidence' in line


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_empty_and_absent_are_distinguishable(cls, method):
    """The whole reason the server keeps them apart; collapsing them here wastes that.
    Absent is silent, empty says the rule matched with nothing to show -- and it is the
    EMPTY side that must never go silent, since it only ever reaches a detail route."""
    assert _matched_lines(_render(cls, method)) == []
    assert len(_matched_lines(_render(cls, method, matched_strings=[]))) == 1


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_populated_renders_identifier_offset_length_and_data(cls, method):
    header, first, second = _matched_lines(_render(cls, method, matched_strings=_STRINGS))
    assert header == 'Matched Strings:'
    assert first == '  $stub @ 0x4e (14 bytes): 54 68 69 73 20 70 72 6F 67 72 61 6D 20 63'
    assert second == '  $mz @ 0x0 (512 bytes, truncated): 4D 5A 90 00 ...'


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_truncation_is_marked_only_where_it_applies(cls, method):
    _, first, second = _matched_lines(_render(cls, method, matched_strings=_STRINGS))
    assert 'truncated' not in first
    assert 'truncated' in second


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_block_sits_between_tags_and_download_url(cls, method):
    """Placement is the acceptance criteria — alongside Rule / Tags, not appended last."""
    text = _render(cls, method, matched_strings=_STRINGS, download_url='http://minio/x')
    lines = text.splitlines()
    tags = next(i for i, line in enumerate(lines) if line.startswith('Tags:'))
    matched = next(i for i, line in enumerate(lines) if line.startswith('Matched Strings:'))
    download = next(i for i, line in enumerate(lines) if line.startswith('Download Url:'))
    assert tags < matched < download


@pytest.mark.parametrize('cls,method', PATHS)
def test_an_sdk_without_the_attribute_does_not_raise(cls, method):
    """The dependency pin admits SDKs predating `matched_strings`, and nothing else here
    would catch a bare `result.matched_strings`.

    Every other test in this file builds resources from the INSTALLED SDK, so with a
    paired SDK on the path a bare attribute read passes all of them and then
    AttributeErrors in the field -- on every text-mode hunt command, not just the new
    output. Deleting the attribute is what an older SDK's resource looks like.
    """
    content = dict(_COMMON)
    content['livescan_id' if cls is resources.LiveHuntResult else 'historicalscan_id'] = 3
    result = cls(content)
    # pop, not `del`: on an SDK that never SET the attribute -- exactly the configuration
    # this test models, and one inside the declared pin -- `del` raises AttributeError and
    # the test errors instead of passing.
    result.__dict__.pop('matched_strings', None)
    assert not hasattr(result, 'matched_strings')
    rendered = click.unstyle('\n'.join(getattr(TextOutput(color=False), method)(result, write=False)))
    assert 'Matched Strings' not in rendered
    assert 'Rule: dos_stub_message' in rendered   # the rest of the row still renders


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_dropped_count_is_reported_to_the_user(cls, method):
    """A short list must not read as the whole truth.

    Without this line a user concludes their rule hit twice when it hit 21 times --
    exactly the wrong-inference class the three-state contract exists to prevent.
    """
    lines = _matched_lines(_render(cls, method, matched_strings=_STRINGS,
                                   matched_strings_dropped=19))
    assert lines[-1].strip().startswith('...')
    assert '19 more not shown' in lines[-1]


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_no_dropped_line_when_nothing_was_dropped(cls, method):
    rendered = _render(cls, method, matched_strings=_STRINGS)
    assert 'not shown' not in rendered


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_dropped_line_does_not_fabricate_a_strings_block(cls, method):
    """A dropped count with no strings is not a thing the server can send -- the
    first string is always kept -- but rendering must not invent a block if it did."""
    rendered = _render(cls, method, matched_strings=None, matched_strings_dropped=19)
    assert 'Matched Strings' not in rendered


@pytest.mark.parametrize('cls,method', PATHS)
def test_older_sdk_without_the_dropped_attribute_does_not_raise(cls, method):
    """Same pin as matched_strings: the dependency floor admits SDKs without it."""
    content = dict(_COMMON, matched_strings=_STRINGS)
    content['livescan_id' if cls is resources.LiveHuntResult else 'historicalscan_id'] = 3
    result = cls(content)
    result.__dict__.pop('matched_strings_dropped', None)   # see the sibling test: not `del`
    assert not hasattr(result, 'matched_strings_dropped')
    rendered = click.unstyle('\n'.join(getattr(TextOutput(color=False), method)(result, write=False)))
    assert 'Matched Strings:' in rendered
    assert 'not shown' not in rendered


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_empty_list_with_a_dropped_count_does_not_claim_no_evidence(cls, method):
    """Contradictory input must not produce a confident false statement.

    The analyzer keeps a match's first string, so this should be unreachable -- but the
    renderer trusted that invariant while asserting "matched without byte evidence" AND
    discarding the count. Report what is certain instead.
    """
    line, = _matched_lines(_render(cls, method, matched_strings=[],
                                   matched_strings_dropped=19))
    assert 'without byte evidence' not in line, 'must not assert a rule property'
    assert '19' in line and 'withheld' in line, 'the count must survive'


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_empty_list_without_a_count_still_says_no_evidence(cls, method):
    """The normal empty case is unchanged."""
    line, = _matched_lines(_render(cls, method, matched_strings=[]))
    assert 'without byte evidence' in line


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_control_characters_in_data_are_neutralised(cls, method):
    """`data` is sample-derived, so it is the one attacker-controlled field here.

    yara escapes non-printables upstream and the analyzer keeps that rendering, so valid
    data never contains a raw control byte -- but that guarantee lives in another repo.
    A CSI sequence reaching a terminal unescaped could repaint or clear an analyst's
    screen, so the renderer neutralises rather than trusting.
    """
    # \x9b is the 8-bit CSI and is the reason this whitelists printable ASCII rather than
    # blacklisting C0: an earlier version stopped at \x7f and let it through, so `\x9b2J`
    # still cleared the screen -- a hole in the exact byte the sanitiser exists to block.
    hostile = [{'offset': 0, 'identifier': '$evil', 'length': 9,
                'data': 'A\x1b[2JB\r\nC\x00D\x9b2JE\u00e9F', 'truncated': False}]
    rendered = _render(cls, method, matched_strings=hostile)
    for bad in ('\x1b', '\x9b', '\r', '\n\n', '\x00', '\u00e9'):
        assert bad not in rendered.split('Matched Strings:')[1], repr(bad)
    # the surviving printable bytes still render, so a legitimate match is unharmed
    assert 'A.[2JB..C.D.2JE.F' in rendered


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_ordinary_data_is_untouched_by_the_sanitiser(cls, method):
    """The escaping is a no-op on what yara actually emits."""
    rendered = _render(cls, method, matched_strings=_STRINGS)
    assert '54 68 69 73 20 70 72 6F 67 72 61 6D 20 63' in rendered


@needs_sdk_fields
@pytest.mark.parametrize('cls,method', PATHS)
def test_output_is_ascii_only(cls, method):
    """stdout under a C/POSIX locale replaces non-ASCII with '?'. Nothing here needs it."""
    rendered = _render(cls, method, matched_strings=_STRINGS, matched_strings_dropped=19)
    block = '\n'.join(_matched_lines(rendered))
    assert block.isascii(), [c for c in block if not c.isascii()]
