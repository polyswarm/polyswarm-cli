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
* the ``--include-counts`` wire plumbing: the kwarg is passed ONLY when
  flagged (an SDK at the pin's floor has a zero-argument ``ruleset_list``, so
  the unflagged path must not send it), asserted through an autospec'd mock so
  the call is signature-checked against the installed SDK.
"""
import io
import types
from unittest import TestCase, mock

from click.testing import CliRunner

from polyswarm.client import polyswarm as client
from polyswarm.formatters import text
from polyswarm_api import resources


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

    def test_ruleset_tracking_fields_render_with_zero_distinct_from_absent(self):
        rendered = self._render('ruleset', _ruleset(
            favorite=True, favorited_at='2026-08-20T12:00:00+00:00', rule_count=0,
            historical_hunt_count=0, new_results_count=3))
        assert 'Favorite: yes' in rendered
        # parse_isoformat: the SDK hands the formatter a datetime, not the wire string
        assert 'Favorited at: 2026-08-20 12:00:00+00:00' in rendered
        assert 'Rules in ruleset: 0' in rendered
        assert 'Historical hunts triggered: 0' in rendered
        assert 'New live results in window: 3' in rendered

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


class RulesListIncludeCountsFlagTest(TestCase):
    """`rules list --include-counts` passes ``include_counts=True``; the
    UNFLAGGED run passes nothing at all — an installed SDK at the pin's floor
    (4.3.0) has a zero-argument ``ruleset_list``, so plain `rules list` must
    keep working there and only the flag may require the new SDK. autospec
    makes both assertions signature checks against the installed SDK."""

    def _run(self, args):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.ruleset_list',
                        autospec=True, return_value=iter(())) as ruleset_list:
            result = CliRunner().invoke(
                client.polyswarm_cli,
                ['-a', '1' * 32, '-u', 'http://ai:9696/v3', '-c', 'gamma',
                 'rules', 'list'] + args,
                catch_exceptions=False)
        assert result.exit_code == 0, result.output
        return ruleset_list

    def test_flag_sends_include_counts_true(self):
        ruleset_list = self._run(['--include-counts'])
        ruleset_list.assert_called_once_with(mock.ANY, include_counts=True)

    def test_no_flag_passes_no_kwargs_at_all(self):
        ruleset_list = self._run([])
        ruleset_list.assert_called_once_with(mock.ANY)
