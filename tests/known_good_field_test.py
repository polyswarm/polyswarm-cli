"""Pure-unit rendering tests for the known_good field on an artifact instance.

No CliRunner / VCR — these drive the text formatter directly with a constructed
ArtifactInstance (the SDK resource), asserting that a known-good binary renders
its flagging feeds and a "Known good" status instead of the misleading
"no engines responded — rescan now" message, and that a normal instance is
unchanged.
"""
import click
from polyswarm_api import resources

from polyswarm.formatters.text import TextOutput

SHA = 'a' * 64


def _instance(**overrides):
    content = {
        'sha256': SHA, 'md5': 'c' * 32, 'sha1': 'b' * 40,
        'mimetype': 'application/x-dosexec', 'size': 68, 'extended_type': '',
        'first_seen': '2020-01-01T00:00:00', 'upload_url': '', 'metadata': [],
        'id': '111', 'community': 'gamma', 'assertions': [], 'votes': [],
        'failed': False, 'window_closed': True, 'polyscore': None,
    }
    content.update(overrides)
    return resources.ArtifactInstance(content)


def _render(instance):
    return click.unstyle('\n'.join(TextOutput(color=False).artifact_instance(instance, write=False)))


class TestKnownGoodTextRendering:
    def test_known_good_instance_renders_feeds_and_status(self):
        feeds = [
            {'tool': 'winget', 'tool_metadata': {}, 'created': '2026-06-11T00:00:00',
             'updated': '2026-06-11T00:00:00'},
            {'tool': 'nsrl', 'tool_metadata': {}, 'created': '2026-06-11T00:00:00',
             'updated': '2026-06-11T00:00:00'},
        ]
        text = _render(_instance(known_good=feeds))
        # Feeds are listed (sorted) and the status reflects known-good.
        assert 'known-good binary (flagged by: nsrl, winget); it is not scanned.' in text
        assert 'Status: Known good' in text
        # A known-good binary must NOT be told to rescan / that no engines responded.
        assert 'trigger a rescan' not in text

    def test_normal_instance_unchanged(self):
        text = _render(_instance())
        assert 'known-good' not in text.lower()
        assert 'Status: Known good' not in text
        # The pre-existing window-closed rendering still applies.
        assert 'Status: Assertion window closed' in text


class TestKnownGoodStateRendering:
    """A known-good-bypassed scan is signalled by state == 'KNOWN_GOOD' even when
    the instance carries no flagging-feed metadata (no matching KnownGood)."""

    def test_state_known_good_without_feeds(self):
        text = _render(_instance(state='KNOWN_GOOD'))
        # Rendered as known-good even with no feeds to attribute it to...
        assert 'This artifact is a known-good binary; it is not scanned.' in text
        assert 'Status: Known good' in text
        # ...and never told to rescan / that no engines responded.
        assert 'trigger a rescan' not in text
        assert 'No engines responded' not in text

    def test_state_known_good_with_feeds_lists_them(self):
        feeds = [{'tool': 'winget', 'tool_metadata': {},
                  'created': '2026-06-11T00:00:00', 'updated': '2026-06-11T00:00:00'}]
        text = _render(_instance(state='KNOWN_GOOD', known_good=feeds))
        # When feeds are present the richer message still lists them.
        assert 'known-good binary (flagged by: winget); it is not scanned.' in text
        assert 'Status: Known good' in text

    def test_non_known_good_state_unchanged(self):
        text = _render(_instance(state='SETTLED'))
        assert 'known-good' not in text.lower()
        assert 'Status: Known good' not in text
