"""The hunt-page tracking legs of the text formatter, and the flag that
reaches them.

Pins three contracts:

* the rendering legs against REAL SDK resources built from literal dicts (not
  hand-built namespaces): the getattr guards convert an attribute-name
  mismatch into silent omission, so only real resources couple these tests to
  the SDK's actual attribute names — and they additionally pin that
  ``favorited_at`` / ``rule_modified`` arrive as parsed datetimes;
* the old-SDK degradation path — a result object without the attributes at
  all (SimpleNamespace on purpose: an installed SDK predating the fields has
  no such attributes to build from) renders without raising and simply omits
  the new lines; and
* the command plumbing: an UNFILTERED ``rules list`` still calls a
  zero-argument ``ruleset_list()`` (the pin's floor, 4.3.0, has exactly
  that signature, so the common invocation needs no new SDK behaviour),
  a FILTERED one forwards exactly the filters given, ``live feed``
  forwards ``--livescan-id`` / ``--max-results`` only when passed, and
  ``rules favorite`` renders the toggle response and converts the
  machine-readable FAVORITE_LIMIT refusal into a clean message. All are
  asserted through autospec'd mocks so every call is signature-checked
  against the installed SDK; the options that DO need the paired SDK are
  pinned to degrade with a clean upgrade message on the floor.
"""
import io
import pathlib
import types
from unittest import TestCase, mock

from click.testing import CliRunner

from polyswarm.client import polyswarm as client
from polyswarm.client import utils
from polyswarm.formatters import text
from polyswarm_api import exceptions, resources

# The favorite surface ships in the paired SDK change; the pin's floor
# (published 4.3.0) has neither the method nor the resource. These tests must
# stay honest on BOTH installs: everything that needs the new surface skips
# on the floor (where `rules favorite` itself degrades to the clean upgrade
# message its own floor test pins with create=True).
# Two guards, deliberately as NARROW as each dependency: the command tests
# need only the METHOD (keying them on the resource too would let a resource
# rename silently skip the whole command suite while CI stays green), and the
# formatter fixture tests need only the RESOURCE class they instantiate.
from tests._sdk_guards import (                      # noqa: E402
    needs_favorite_method as _needs_favorite_method,
    needs_favorite_resource as _needs_favorite_resource,
    needs_live_feed_options as _needs_live_feed_options,
    needs_provenance_fields as _needs_provenance_fields,
    needs_ruleset_list_filters as _needs_ruleset_list_filters,
    needs_tracking_fields as _needs_tracking_fields,
)


def _ruleset(**overrides):
    content = dict(id='5', livescan_id=None, livescan_created=None, name='n',
                   description='d', created='2026-08-20T00:00:00+00:00',
                   modified='2026-08-20T00:00:00+00:00', deleted=False, yara=None)
    content.update(overrides)
    return resources.YaraRuleset(content, api=None)


def _hunt(**overrides):
    content = dict(id='9', status='PENDING', progress=0.0, active=None,
                   created='2026-08-20T00:00:00+00:00', summary=None,
                   results_csv_uri=None, ruleset_name='n', yara=None)
    content.update(overrides)
    return resources.HistoricalHunt(content, api=None)


def _old_sdk_ruleset():
    """A result parsed by an SDK release that predates the tracking fields:
    the attributes are ABSENT, not None — SimpleNamespace is deliberate, since
    the installed (new) SDK cannot build such an object."""
    return types.SimpleNamespace(
        id='5', livescan_id=None, livescan_created=None, name='n',
        description='d', created='c', modified='m', yara=None)


def _old_sdk_hunt():
    return types.SimpleNamespace(
        id='9', status='PENDING', progress=None, active=None, created='c',
        summary=None, results_csv_uri=None, ruleset_name='n', yara=None)


class FormatterHuntFieldsTest(TestCase):
    def _render(self, method, result, **kwargs):
        out = io.StringIO()
        getattr(text.TextOutput(color=False, output=out), method)(result, **kwargs)
        return out.getvalue()

    @_needs_tracking_fields
    def test_ruleset_tracking_fields_render_with_zero_distinct_from_absent(self):
        rendered = self._render('ruleset', _ruleset(
            favorite=True, favorited_at='2026-08-20T12:00:00+00:00', rule_count=0,
            historical_hunt_count=0, new_results_count=3))
        assert 'Favorite: yes' in rendered
        # parse_isoformat: the SDK hands the formatter a datetime, not the wire string
        assert 'Favorited at: 2026-08-20 12:00:00+00:00' in rendered
        assert 'Rules in ruleset: 0' in rendered
        assert 'Historical hunts triggered: 0' in rendered
        assert 'New live results (last 24h): 3' in rendered

    @_needs_tracking_fields
    def test_ruleset_staleness_marker_renders_beside_the_count(self):
        # The stored badge's marker: how fresh the number is. Rendered only
        # with a count (the server sends them together).
        rendered = self._render('ruleset', _ruleset(
            new_results_count=0,
            new_results_counted_at='2026-08-25T12:00:00+00:00'))
        assert 'New live results (last 24h): 0' in rendered
        assert 'New-results count refreshed at: 2026-08-25 12:00:00+00:00' in rendered

    @_needs_favorite_resource
    def test_ruleset_favorite_response_renders_state_and_budget(self):
        rendered = self._render('ruleset_favorite', resources.YaraRulesetFavorite(
            {'id': '5', 'favorite': True,
             'favorited_at': '2026-08-25T12:00:00+00:00',
             'favorites_used': 3, 'favorites_limit': 5}, api=None))
        assert 'Ruleset Id: 5' in rendered
        assert 'Favorite: yes' in rendered
        assert 'Favorited at: 2026-08-25 12:00:00+00:00' in rendered
        assert 'Favorites used: 3 of 5' in rendered

    @_needs_favorite_resource
    def test_ruleset_unfavorite_response_renders_no_state(self):
        rendered = self._render('ruleset_favorite', resources.YaraRulesetFavorite(
            {'id': '5', 'favorite': False, 'favorited_at': None,
             'favorites_used': 2, 'favorites_limit': 5}, api=None))
        assert 'Favorite: no' in rendered
        assert 'Favorited at' not in rendered
        assert 'Favorites used: 2 of 5' in rendered

    @_needs_tracking_fields
    def test_ruleset_none_and_false_fields_are_omitted(self):
        rendered = self._render('ruleset', _ruleset(
            favorite=False, favorited_at=None, rule_count=None,
            historical_hunt_count=None, new_results_count=None))
        assert 'Favorite' not in rendered
        assert 'Rules in ruleset' not in rendered
        assert 'Historical hunts triggered' not in rendered
        assert 'New live results' not in rendered

    def test_old_sdk_ruleset_without_the_attributes_renders(self):
        rendered = self._render('ruleset', _old_sdk_ruleset())
        assert 'Ruleset Id: 5' in rendered
        assert 'Favorite' not in rendered

    @_needs_provenance_fields
    def test_hunt_provenance_fields_render_with_the_reference_point(self):
        rendered = self._render('hunt', _hunt(
            rule_id='5', rule_modified='2026-08-20T12:00:00+00:00',
            source_rule_changed=False))
        assert 'Source Ruleset Id: 5' in rendered
        assert 'Source ruleset last modified at freeze: 2026-08-20 12:00:00+00:00' in rendered
        assert 'Source ruleset changed since this hunt froze it: no' in rendered

    def test_hunt_unknown_tri_state_prints_nothing(self):
        rendered = self._render('hunt', _hunt(
            rule_id=None, rule_modified=None, source_rule_changed=None))
        assert 'Source' not in rendered

    def test_old_sdk_hunt_without_the_attributes_renders(self):
        rendered = self._render('hunt', _old_sdk_hunt())
        assert 'Hunt Id: 9' in rendered
        assert 'Source' not in rendered


class RulesListZeroArgTest(TestCase):
    """`rules list` calls a zero-argument ``ruleset_list()`` — the pin's
    floor (4.3.0) has exactly that signature, so the command needs no new SDK
    behaviour at all. autospec makes the assertion a signature check against
    the installed SDK."""

    def test_list_passes_no_kwargs_at_all(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_list',
                        autospec=True, return_value=iter(())) as ruleset_list:
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'list'],
                catch_exceptions=False)
        assert result.exit_code == 0, result.output
        ruleset_list.assert_called_once_with(mock.ANY)

    @_needs_ruleset_list_filters
    def test_filters_are_forwarded_only_when_given(self):
        """A filtered list forwards exactly the filters passed and nothing
        else — the flags default to False, and a False flag must not become
        `favorites_only=False`, which would be a filter the caller never
        asked for."""
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_list',
                        autospec=True, return_value=iter(())) as ruleset_list:
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'list', '--name', 'alpha', '--favorites-only',
                 '--status', 'active', '--has-new-results'],
                catch_exceptions=False)
        assert result.exit_code == 0, result.output
        # All four filters, because autospec is what turns this into a
        # SIGNATURE check against the installed SDK: a kwarg name that only
        # this side renamed would otherwise ship as require_sdk_kwargs
        # refusing on an SDK that does have the surface.
        ruleset_list.assert_called_once_with(
            mock.ANY, name='alpha', status='active',
            favorites_only=True, has_new_results=True)

    def test_filtering_on_a_floor_sdk_is_a_clean_message_not_a_traceback(self):
        """The published floor's ``ruleset_list()`` takes no filters. Using one
        there must produce the upgrade message at exit 2 (the server-refusal
        code), never the TypeError traceback a bare kwarg would raise.

        The floor is simulated by a stand-in with the FLOOR signature, which is
        what the guard inspects."""
        def floor_ruleset_list(self):
            return iter(())

        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_list',
                        floor_ruleset_list):
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'list', '--name', 'alpha'])
        assert result.exit_code == 2, result.output
        assert f'newer than {utils.SDK_FLOOR}' in result.output
        assert 'Traceback' not in result.output


class LiveFeedOptionsTest(TestCase):
    """`live feed` — the badge's drill-down (--livescan-id) and its bound
    (--max-results). Both are forwarded only when passed, so every existing
    invocation reaches the SDK exactly as it did before."""

    def _invoke(self, *extra):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.live_feed',
                        autospec=True, return_value=iter(())) as live_feed:
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'live', 'feed', *extra],
                catch_exceptions=False)
        return result, live_feed

    def test_plain_feed_forwards_neither_new_kwarg(self):
        result, live_feed = self._invoke()
        assert result.exit_code == 0, result.output
        _, kwargs = live_feed.call_args
        assert 'livescan_id' not in kwargs and 'max_results' not in kwargs
        # the default window is 86400 SECONDS (24h), passed positionally — the
        # wire is seconds and stays seconds, so the CLI default carries the 24h
        assert live_feed.call_args[0][1] == 86400

    @_needs_live_feed_options
    def test_livescan_id_and_max_results_are_forwarded(self):
        result, live_feed = self._invoke(
            '--livescan-id', '72927285313305230', '--max-results', '5')
        assert result.exit_code == 0, result.output
        _, kwargs = live_feed.call_args
        # click.INT, and Python ints are arbitrary precision — a 17-digit id
        # survives exactly, which is the whole reason the server renders it as
        # a string for JS consumers.
        assert kwargs['livescan_id'] == 72927285313305230
        assert kwargs['max_results'] == 5

    def test_zero_max_results_is_unbounded_and_never_reaches_the_sdk(self):
        """--max-results 0 is documented as the pre-existing unbounded
        behaviour, so it must not be forwarded — and therefore must not trip the
        floor guard for an invocation the floor already serves."""
        result, live_feed = self._invoke('--max-results', '0')
        assert result.exit_code == 0, result.output
        _, kwargs = live_feed.call_args
        assert 'max_results' not in kwargs

    def test_zero_max_results_does_not_trip_the_floor_guard(self):
        def floor_live_feed(self, since=None, rule_name=None, family=None,
                            polyscore_lower=None, polyscore_upper=None,
                            community=None):
            return iter(())

        with mock.patch('polyswarm_api.api.PolyswarmAPI.live_feed',
                        floor_live_feed):
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'live', 'feed', '--max-results', '0'])
        assert result.exit_code == 0, result.output

    def test_a_negative_max_results_is_refused_at_the_interface(self):
        result = CliRunner().invoke(
            client.polyswarm_cli,
            ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
             'live', 'feed', '--max-results', '-1'])
        assert result.exit_code != 0

    def test_a_non_numeric_livescan_id_is_refused_before_the_server(self):
        result = CliRunner().invoke(
            client.polyswarm_cli,
            ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
             'live', 'feed', '--livescan-id', 'not-an-id'])
        assert result.exit_code != 0

    def test_new_options_on_a_floor_sdk_are_a_clean_message(self):
        def floor_live_feed(self, since=None, rule_name=None, family=None,
                            polyscore_lower=None, polyscore_upper=None,
                            community=None):
            return iter(())

        with mock.patch('polyswarm_api.api.PolyswarmAPI.live_feed',
                        floor_live_feed):
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'live', 'feed', '--livescan-id', '7'])
        assert result.exit_code == 2, result.output
        assert f'newer than {utils.SDK_FLOOR}' in result.output
        assert 'Traceback' not in result.output


class RulesFavoriteCommandTest(TestCase):
    """`rules favorite` — the CLI leg of the favorite capability: renders the
    toggle response (state + server-owned budget counters), passes the right
    boolean for --unfavorite, and converts the machine-readable FAVORITE_LIMIT
    refusal into a clean actionable message instead of a traceback."""

    def _invoke(self, args, side_effect=None, return_value=None):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_favorite',
                        autospec=True, side_effect=side_effect,
                        return_value=return_value) as toggle:
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'favorite'] + args,
                catch_exceptions=False)
        return result, toggle

    @staticmethod
    def _response(favorite):
        return resources.YaraRulesetFavorite(
            {'id': '5', 'favorite': favorite,
             'favorited_at': '2026-08-25T12:00:00+00:00' if favorite else None,
             'favorites_used': 1, 'favorites_limit': 5}, api=None)

    @_needs_favorite_method
    @_needs_favorite_resource
    def test_favorite_calls_the_sdk_and_renders_the_budget(self):
        result, toggle = self._invoke(['5'], return_value=self._response(True))
        assert result.exit_code == 0, result.output
        toggle.assert_called_once_with(mock.ANY, 5, True)
        assert 'Favorite: yes' in result.output
        assert 'Favorites used: 1 of 5' in result.output

    @_needs_favorite_method
    @_needs_favorite_resource
    def test_unfavorite_flag_flips_the_boolean(self):
        result, toggle = self._invoke(['5', '--unfavorite'],
                                      return_value=self._response(False))
        assert result.exit_code == 0, result.output
        toggle.assert_called_once_with(mock.ANY, 5, False)
        assert 'Favorite: no' in result.output

    @_needs_favorite_method
    def test_favorite_limit_refusal_is_a_clean_message_at_exit_2(self):
        # Exit 2 is the central mapping's code for this, never 1; exit 1 is
        # reserved for no-results/not-found. The friendly message rides a CLI
        # PolyswarmException so ExceptionHandlingGroup logs it cleanly.
        request = mock.Mock()
        request.errors = {'code': 'FAVORITE_LIMIT',
                          'favorites_used': 5, 'favorites_limit': 5}
        refusal = exceptions.RequestException(request)
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_favorite',
                        autospec=True, side_effect=refusal):
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'favorite', '5'])
        assert result.exit_code == 2, result.output
        assert 'Favorite limit reached (5 of 5 used)' in result.output
        assert '--unfavorite' in result.output            # names the way out
        assert 'Traceback' not in result.output

    @_needs_favorite_method
    def test_favorite_limit_without_counters_uses_the_server_message(self):
        # The counters are advisory; an envelope can carry the code without
        # them. Interpolating them unguarded rendered "(None of None used)" at
        # the user, so the server's own message is the fallback.
        request = mock.Mock()
        request.errors = {'code': 'FAVORITE_LIMIT'}
        request.result = 'Favorite limit reached (5 of 5 used).'
        refusal = exceptions.RequestException(request)
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_favorite',
                        autospec=True, side_effect=refusal):
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'favorite', '5'])
        assert result.exit_code == 2, result.output
        assert 'None of None' not in result.output
        assert 'Favorite limit reached (5 of 5 used).' in result.output
        assert '--unfavorite' in result.output

    @_needs_favorite_method
    def test_favorite_limit_on_a_request_without_result_still_has_no_traceback(self):
        # A Mock has every attribute, so the test above cannot fail on a missing
        # `.result`. This one uses a real object that genuinely lacks it — the
        # handler exists to avoid a traceback and must not raise one reaching
        # for its own fallback.
        class BareRequest:
            errors = {'code': 'FAVORITE_LIMIT'}

        refusal = exceptions.RequestException(BareRequest())
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_favorite',
                        autospec=True, side_effect=refusal):
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'favorite', '5'])
        assert result.exit_code == 2, result.output
        assert 'Traceback' not in result.output
        assert 'None' not in result.output
        assert '--unfavorite' in result.output

    def test_favorite_on_the_floor_sdk_degrades_cleanly(self):
        # The declared floor (published 4.3.0) has no ruleset_favorite: the
        # command must fail with a clean upgrade message at exit 2, never an
        # AttributeError traceback — CI's branch-name SDK install can never
        # surface this, so the test simulates the floor by nulling the method.
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_favorite',
                        new=None, create=True):
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'favorite', '5'])
        assert result.exit_code == 2, result.output
        assert (f'requires a polyswarm-api release newer than {utils.SDK_FLOOR}'
                in result.output)
        assert 'AttributeError' not in result.output

    @_needs_favorite_method
    def test_other_refusals_still_raise(self):
        request = mock.Mock()
        request.errors = None
        refusal = exceptions.RequestException(request)
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_favorite',
                        autospec=True, side_effect=refusal):
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'favorite', '5'])
        assert result.exit_code == 2                      # PolyswarmException family
        assert 'FAVORITE_LIMIT' not in result.output

class SdkFloorConstantTest(TestCase):
    """``utils.SDK_FLOOR`` must equal the lower bound in ``pyproject.toml``.

    specs/05-sdk-contract.md makes the pin the one authoritative floor, and the
    constant only exists so the guard messages can name it. Nothing else ties
    the two together: the follow-up bump edits the pin, and a stale constant
    would leave every upgrade message naming the wrong version while the suite
    stayed green — the exact drift specs/05 says the pin exists to prevent."""

    def test_the_constant_matches_the_pin(self):
        import re
        pyproject = (pathlib.Path(__file__).resolve().parent.parent
                     / 'pyproject.toml').read_text()
        match = re.search(r'polyswarm_api>=([0-9]+\.[0-9]+\.[0-9]+)', pyproject)
        assert match, 'polyswarm_api pin not found in pyproject.toml'
        assert utils.SDK_FLOOR == match.group(1)
