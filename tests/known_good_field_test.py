"""Pure-unit rendering tests for the known_good field on an artifact instance.

No CliRunner / VCR — these drive the text formatter directly with a constructed
ArtifactInstance (the SDK resource), asserting that a known-good binary — signalled
by its state, the only reliable signal — renders its flagging feeds and a
"Known good" status instead of the misleading "no engines responded — rescan now"
message, that the flagging feeds on their own never make an instance known-good,
that a failure outranks the known-good signal, that a known-good instance which
also carries preserved results reports them instead of claiming it was not
scanned, and that a normal instance is unchanged.
"""
import click
from polyswarm_api import resources

from polyswarm.formatters.text import TextOutput

SHA = 'a' * 64

FEEDS = [
    {'tool': 'commercial', 'tool_metadata': {}, 'created': '2026-06-11T00:00:00',
     'updated': '2026-06-11T00:00:00'},
    {'tool': 'nsrl', 'tool_metadata': {}, 'created': '2026-06-11T00:00:00',
     'updated': '2026-06-11T00:00:00'},
]


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


def _assertion(engine, verdict):
    return {
        'author': '0x' + 'd' * 40, 'author_name': engine, 'engine': {'name': engine},
        'bid': '1000000000000000', 'mask': True, 'metadata': None, 'verdict': verdict,
    }


def _render(instance):
    return click.unstyle('\n'.join(TextOutput(color=False).artifact_instance(instance, write=False)))


class TestKnownGoodTextRendering:
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
        text = _render(_instance(state='KNOWN_GOOD', known_good=FEEDS))
        # When feeds are present the richer message still lists them (sorted).
        assert 'known-good binary (flagged by: commercial, nsrl); it is not scanned.' in text
        assert 'Status: Known good' in text

    def test_known_good_with_results_reports_them_instead_of_not_scanned(self):
        # A previously scanned instance reconciled to KNOWN_GOOD keeps its assertions,
        # detections and PolyScore. The assertion loop is not gated on the known-good
        # branch, so the old copy printed "it is not scanned." immediately above the
        # per-engine verdicts — a self-contradiction. The Detections line must state
        # both facts: still a known-good binary, and here is what the engines found.
        assertions = [_assertion('engine-a', True), _assertion('engine-b', False)]
        text = _render(_instance(state='KNOWN_GOOD', known_good=FEEDS, assertions=assertions,
                                 polyscore=0.9))
        assert ('Detections: This artifact is a known-good binary (flagged by: commercial, nsrl); '
                '1/2 engines reported malicious.') in text
        assert 'it is not scanned' not in text
        # The verdicts that made the old phrasing contradictory still render, as does the
        # known-good status and the preserved PolyScore.
        assert 'engine-a: Malicious' in text
        assert 'engine-b: Clean' in text
        assert 'Status: Known good' in text
        assert 'PolyScore: 0.9' in text

    def test_known_good_with_results_and_no_feeds(self):
        # Same reconciliation without a flagging-feed attribution: the feed clause is
        # orthogonal to the results clause, so dropping one must not drop the other.
        assertions = [_assertion('engine-a', False)]
        text = _render(_instance(state='KNOWN_GOOD', assertions=assertions))
        assert 'Detections: This artifact is a known-good binary; 0/1 engines reported malicious.' in text
        assert 'it is not scanned' not in text
        assert 'Status: Known good' in text

    def test_known_good_with_only_non_responding_engines_is_still_not_scanned(self):
        # Assertions that all declined (mask False) are not results — valid_assertions is
        # empty — so the withheld/never-scanned clause is still the accurate one. Keying
        # the switch on `instance.assertions` instead would render "0/0 engines".
        declined = _assertion('engine-a', None)
        declined['mask'] = False
        text = _render(_instance(state='KNOWN_GOOD', assertions=[declined]))
        assert 'Detections: This artifact is a known-good binary; it is not scanned.' in text
        assert 'engines reported malicious' not in text

    def test_non_known_good_state_unchanged(self):
        text = _render(_instance(state='SETTLED'))
        assert 'known-good' not in text.lower()
        assert 'Status: Known good' not in text

    def test_failed_instance_reports_the_failure_not_known_good(self):
        # A failure outranks the known-good signal: the Detections branch is gated on
        # `not instance.failed` and 'Status: Failed' is ordered ahead of 'Status: Known
        # good'. Dropping either would tell the user a failed lookup is a benign binary.
        text = _render(_instance(state='KNOWN_GOOD', known_good=FEEDS, failed=True,
                                 failed_reason='artifact storage unavailable'))
        assert 'Detections: This scan has failed. Please try again.' in text
        assert 'Status: Failed' in text
        assert 'Failure Reason: artifact storage unavailable' in text
        # Never claim the artifact is a known-good binary that was not scanned.
        assert 'it is not scanned' not in text
        assert 'Status: Known good' not in text


class TestKnownGoodFeedsAreNotTheSignal:
    """The flagging-feed list is served for every instance whose sha256 matches a
    known-good record — including one that was scanned before it was flagged — so it
    only shapes the message for an instance already known-good by state."""

    def test_feeds_without_known_good_state_are_ignored(self):
        text = _render(_instance(state='SETTLED', known_good=FEEDS))
        assert 'known-good' not in text.lower()
        assert 'Status: Known good' not in text
        assert 'Status: Assertion window closed' in text

    def test_feeds_without_any_state_render_as_an_ordinary_instance(self):
        # The no-state path: an older server omits `state` (parses to None) and an SDK
        # predating `.state` has no such attribute at all. Both leave the feed list as
        # the only known-good hint, and it must not be used — this is the assertion that
        # catches the removed feed-list fallback being reintroduced.
        no_state = _instance(known_good=FEEDS)
        older_sdk = _instance(known_good=FEEDS)
        del older_sdk.state
        for instance in (no_state, older_sdk):
            text = _render(instance)
            assert 'known-good' not in text.lower()
            assert 'Status: Known good' not in text
            # Rendered exactly like any other window-closed instance with no assertions.
            assert 'Detections: No engines responded to this scan. You can trigger a rescan now.' in text
            assert 'Status: Assertion window closed' in text

    def test_scanned_instance_with_feeds_reports_its_detections(self):
        assertions = [_assertion('engine-a', True), _assertion('engine-b', False)]
        text = _render(_instance(state='SETTLED', known_good=FEEDS, assertions=assertions,
                                 polyscore=0.9))
        # The real scan results are reported, never overwritten by a "not scanned" claim.
        assert 'Detections: 1/2 engines reported malicious' in text
        assert 'it is not scanned' not in text
