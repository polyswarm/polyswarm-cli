"""Skip guards keyed on the SDK surface a test actually needs.

``pyproject.toml`` pins a FLOOR, not an exact SDK, so the suite runs against
either the floor or a newer paired SDK and a test needing a surface the floor
lacks must SKIP there — not fail, and above all not pass vacuously. The full
convention, including why the guard is keyed on the narrowest dependency, is in
``specs/04-testing.md`` §Staying honest on both installs the pin permits.

Shared because two modules need the same guards: the formatter unit tests build
resources directly, and the cassette tests render CLI output whose lines only
appear when the SDK parses the underlying attribute."""
import unittest

from polyswarm_api import resources
from polyswarm_api.api import PolyswarmAPI

_RULESET = {'id': '0', 'livescan_id': None, 'livescan_created': None,
            'name': 'n', 'description': 'd', 'deleted': False,
            'created': '2026-08-20T00:00:00+00:00',
            'modified': '2026-08-20T00:00:00+00:00', 'yara': None,
            # the probed keys are present so the guard does not depend on the
            # SDK assigning absent ones
            'rule_count': 1, 'favorite': False, 'historical_hunt_count': 0}
_HUNT = {'id': '0', 'status': 'PENDING', 'progress': 0.0, 'active': None,
         'created': '2026-08-20T00:00:00+00:00', 'summary': None,
         'results_csv_uri': None, 'ruleset_name': 'n', 'yara': None,
         'rule_id': '1', 'rule_modified': None, 'source_rule_changed': False}

# Keyed on the METHOD, never also on the resource class: that would let a
# resource rename silently skip the whole command suite while CI stays green.
needs_favorite_method = unittest.skipUnless(
    hasattr(PolyswarmAPI, 'ruleset_favorite'),
    'paired SDK method (ruleset_favorite) not installed')
needs_favorite_resource = unittest.skipUnless(
    hasattr(resources, 'YaraRulesetFavorite'),
    'paired SDK resource (YaraRulesetFavorite) not installed')

# Keyed on the ATTRIBUTE, not the class: YaraRuleset and HistoricalHunt exist on
# the floor and simply do not parse these keys, so a class-level guard does not
# skip — the render assertions fail, and an absence-asserting test passes
# vacuously, which looks like coverage while pinning nothing.
needs_tracking_fields = unittest.skipUnless(
    hasattr(resources.YaraRuleset(_RULESET, api=None), 'rule_count'),
    'paired SDK does not parse the ruleset tracking fields')
needs_provenance_fields = unittest.skipUnless(
    hasattr(resources.HistoricalHunt(_HUNT, api=None), 'source_rule_changed'),
    'paired SDK does not parse the hunt provenance fields')
