"""Tests for the search CLI commands.

These tests mock the SDK methods directly to keep the test runtime
self-contained (no live artifact-index, no VCR cassettes).
"""
from unittest import TestCase, mock
from unittest.mock import MagicMock

from click.testing import CliRunner
from polyswarm_api import exceptions as api_exceptions

from polyswarm.client import polyswarm as client


_API_KEY = '1' * 32
_API_URL = 'http://artifact-index-e2e:9696/v3'
_COMMUNITY = 'gamma'

_FOUND_HASH = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
_EMPTY_HASH = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0a'


def _fake_instance(sha256=_FOUND_HASH):
    obj = MagicMock()
    obj.id = 789
    obj.json = {'id': 789, 'sha256': sha256}
    return obj


def _empty_search():
    """A lazy generator mirroring the SDK's 4.x search semantics: calling the
    method does nothing; the 204 surfaces as NoResultsException on iteration."""
    raise api_exceptions.NoResultsException(None, 'The request returned no results.')
    yield  # pragma: no cover — makes this function a generator


class SearchHashesCliTest(TestCase):
    def setUp(self):
        self.cli = CliRunner()

    def _run(self, *cmd):
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY,
             '--output-format', 'json'] + list(cmd),
            catch_exceptions=False,
        )

    def test_search_hashes_mixed_found_and_empty(self):
        """Multi-hash search with one empty result must not abort on the first
        empty item: the found instance is still rendered, every hash is
        attempted, and the run ends with the executor's aggregate
        NotFoundException (exit 1), not the raw SDK NoResultsException.
        The empty hash comes FIRST to pin the no-abort behaviour."""
        instance = _fake_instance()

        def fake_search(hash_, hash_type=None):
            if hash_ == _FOUND_HASH:
                return iter([instance])
            return _empty_search()

        with mock.patch('polyswarm_api.api.PolyswarmAPI.search',
                        side_effect=fake_search) as m:
            result = self._run('search', 'hash', _EMPTY_HASH, _FOUND_HASH)
        assert m.call_count == 2
        assert '"id": 789' in result.output
        assert 'One or more items did not return any results' in result.output
        assert result.exit_code == 1, result.output
