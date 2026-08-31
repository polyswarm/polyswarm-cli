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
  zero-argument ``ruleset_list()`` (a False flag is not a filter), a
  FILTERED one forwards exactly the filters given, ``live feed`` forwards
  ``--livescan-id`` / ``--max-results`` only when passed, and ``rules
  favorite`` renders the toggle response and converts the machine-readable
  FAVORITE_LIMIT refusal into a clean message. All are asserted through
  autospec'd mocks, so every call is signature-checked against the SDK the
  pin actually installs.
"""
import io
import pathlib
import types
from unittest import TestCase, mock

from click.testing import CliRunner

from polyswarm.client import polyswarm as client
from polyswarm.formatters import text
from polyswarm_api import exceptions, resources



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






class FormatterHuntFieldsTest(TestCase):
    def _render(self, method, result, **kwargs):
        out = io.StringIO()
        getattr(text.TextOutput(color=False, output=out), method)(result, **kwargs)
        return out.getvalue()
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
    def test_ruleset_staleness_marker_renders_beside_the_count(self):
        # The stored badge's marker: how fresh the number is. Rendered only
        # with a count (the server sends them together).
        rendered = self._render('ruleset', _ruleset(
            new_results_count=0,
            new_results_counted_at='2026-08-25T12:00:00+00:00'))
        assert 'New live results (last 24h): 0' in rendered
        assert 'New-results count refreshed at: 2026-08-25 12:00:00+00:00' in rendered
    def test_ruleset_favorite_response_renders_state_and_budget(self):
        rendered = self._render('ruleset_favorite', resources.YaraRulesetFavorite(
            {'id': '5', 'favorite': True,
             'favorited_at': '2026-08-25T12:00:00+00:00',
             'favorites_used': 3, 'favorites_limit': 5}, api=None))
        assert 'Ruleset Id: 5' in rendered
        assert 'Favorite: yes' in rendered
        assert 'Favorited at: 2026-08-25 12:00:00+00:00' in rendered
        assert 'Favorites used: 3 of 5' in rendered
    def test_ruleset_unfavorite_response_renders_no_state(self):
        rendered = self._render('ruleset_favorite', resources.YaraRulesetFavorite(
            {'id': '5', 'favorite': False, 'favorited_at': None,
             'favorites_used': 2, 'favorites_limit': 5}, api=None))
        assert 'Favorite: no' in rendered
        assert 'Favorited at' not in rendered
        assert 'Favorites used: 2 of 5' in rendered
    def test_ruleset_none_and_false_fields_are_omitted(self):
        rendered = self._render('ruleset', _ruleset(
            favorite=False, favorited_at=None, rule_count=None,
            historical_hunt_count=None, new_results_count=None))
        assert 'Favorite' not in rendered
        assert 'Rules in ruleset' not in rendered
        assert 'Historical hunts triggered' not in rendered
        assert 'New live results' not in rendered

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



class RulesListZeroArgTest(TestCase):
    """`rules list` calls a zero-argument ``ruleset_list()`` — a False flag
    is not a filter, so an unfiltered list forwards no
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
        # All four, and autospec makes this a SIGNATURE check against the
        # installed SDK: a kwarg only this side renamed fails here rather than
        # reaching the server as a filter it silently ignores.
        ruleset_list.assert_called_once_with(
            mock.ANY, name='alpha', status='active',
            favorites_only=True, has_new_results=True)



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
        """--max-results 0 is the pre-existing unbounded behaviour, so it must not
        be forwarded — omitting it is what already means "no bound"."""
        result, live_feed = self._invoke('--max-results', '0')
        assert result.exit_code == 0, result.output
        _, kwargs = live_feed.call_args
        assert 'max_results' not in kwargs

    def test_zero_since_IS_forwarded_unlike_zero_max_results(self):
        """Both zeros mean "no bound" to the user and take OPPOSITE paths:
        --max-results 0 is dropped before the SDK (above), while --since 0 must
        reach it, because 0 is how the server is told to apply no time filter.
        Fold `since` into the conditional-kwargs block and this breaks."""
        result, live_feed = self._invoke('--since', '0')
        assert result.exit_code == 0, result.output
        assert live_feed.call_args[0][1] == 0


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
        # A namespace, not the SDK resource: TextOutput.ruleset_favorite reads
        # `.id` plus getattrs, so building the real class would make these
        # command tests depend on the RESOURCE and a rename would silently skip
        # the only coverage that `rules favorite` calls the SDK at all.
        return types.SimpleNamespace(
            id='5', favorite=favorite,
            favorited_at='2026-08-25T12:00:00+00:00' if favorite else None,
            favorites_used=1, favorites_limit=5)
    def test_favorite_calls_the_sdk_and_renders_the_budget(self):
        result, toggle = self._invoke(['5'], return_value=self._response(True))
        assert result.exit_code == 0, result.output
        toggle.assert_called_once_with(mock.ANY, 5, True)
        assert 'Favorite: yes' in result.output
        assert 'Favorites used: 1 of 5' in result.output
    def test_unfavorite_flag_flips_the_boolean(self):
        result, toggle = self._invoke(['5', '--unfavorite'],
                                      return_value=self._response(False))
        assert result.exit_code == 0, result.output
        toggle.assert_called_once_with(mock.ANY, 5, False)
        assert 'Favorite: no' in result.output
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

class ExitCodeHierarchyTest(TestCase):
    """`rules favorite`'s non-limit refusals exit 2, and that holds only because
    the SDK's RequestException is a PolyswarmException — the handler catches
    that base BEFORE the transport branch, which matches the bare name
    'RequestException' against the MRO and would exit 1 with "contact support".
    Reparent it in the SDK and every fixable 4xx starts giving that advice, so
    the dependency is pinned here rather than inferred."""

    def test_request_exception_is_caught_as_a_polyswarm_exception(self):
        assert issubclass(exceptions.RequestException,
                          exceptions.PolyswarmException)


