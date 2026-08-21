"""The hunt-page tracking legs of the text formatter.

Pins two contracts:

* the getattr guards — the formatter renders results parsed by an SDK release
  that predates the fields (attributes absent entirely) without raising, and
  simply omits the new lines; and
* the None/False/0 semantics — ``rule_count=0`` and ``historical_hunt_count=0``
  render as real zeros (distinct from an omitted None), ``favorite=False``
  prints nothing (truthy-only leg), and ``source_rule_changed``'s label names
  its reference point ("since this hunt froze it") so it can't read as
  "edited recently".
"""
import io
import types
from unittest import TestCase

from polyswarm.formatters import text


def _ruleset(**overrides):
    base = dict(id='5', livescan_id=None, livescan_created=None, name='n',
                description='d', created='c', modified='m', yara=None)
    base.update(overrides)
    return types.SimpleNamespace(**base)


def _hunt(**overrides):
    base = dict(id='9', status='PENDING', progress=None, active=None,
                created='c', summary=None, results_csv_uri=None,
                ruleset_name='n', yara=None)
    base.update(overrides)
    return types.SimpleNamespace(**base)


class FormatterHuntFieldsTest(TestCase):
    def _render(self, method, result, **kwargs):
        out = io.StringIO()
        getattr(text.TextOutput(color=False, output=out), method)(result, **kwargs)
        return out.getvalue()

    def test_ruleset_tracking_fields_render_with_zero_distinct_from_absent(self):
        rendered = self._render('ruleset', _ruleset(
            favorite=True, favorited_at='2026-08-20', rule_count=0,
            historical_hunt_count=0, new_results_count=3))
        assert 'Favorite: yes' in rendered
        assert 'Favorited at: 2026-08-20' in rendered
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
        rendered = self._render('ruleset', _ruleset())
        assert 'Ruleset Id: 5' in rendered
        assert 'Favorite' not in rendered

    def test_hunt_provenance_fields_render_with_the_reference_point(self):
        rendered = self._render('hunt', _hunt(
            rule_id='5', rule_modified='2026-08-20', source_rule_changed=False))
        assert 'Source Ruleset Id: 5' in rendered
        assert 'Source ruleset last modified at freeze: 2026-08-20' in rendered
        assert 'Source ruleset changed since this hunt froze it: no' in rendered

    def test_hunt_unknown_tri_state_prints_nothing(self):
        rendered = self._render('hunt', _hunt(
            rule_id=None, rule_modified=None, source_rule_changed=None))
        assert 'Source' not in rendered

    def test_old_sdk_hunt_without_the_attributes_renders(self):
        rendered = self._render('hunt', _hunt())
        assert 'Hunt Id: 9' in rendered
        assert 'Source' not in rendered
