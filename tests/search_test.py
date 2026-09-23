"""Tests for the search CLI commands.

These tests mock the SDK methods directly to keep the test runtime
self-contained (no live artifact-index, no VCR cassettes).
"""
import json
from unittest import TestCase, mock
from unittest.mock import MagicMock

from click.testing import CliRunner
from polyswarm_api import exceptions as api_exceptions
from polyswarm_api import resources

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


def _ioc_artifact_row():
    """A reverse-IOC artifact row as the server returns it under
    ``with_artifacts``: a metadata-search document cut to artifact.* and the
    scan summary."""
    return {
        'artifact': {
            'created': '2026-06-05T19:01:38.104756+00:00',
            'id': '31542742786663251',
            'md5': '5d3bc3c626be6b6f59195afc4ab80fc8',
            'sha1': 'f1d73dcb1286cf42e707b5d7fcf918dd45290411',
            'sha256': _FOUND_HASH,
        },
        'scan': {
            'detections': {'benign': 0, 'malicious': 1, 'total': 1},
            'filename': ['artifact'],
            'latest_scan': {'created': '2026-06-05T19:01:38.104756+00:00',
                            'polyscore': 0.97},
            'mimetype': {'extended': 'EICAR virus test files', 'mime': 'text/plain'},
        },
        'polyunite': {'malware_family': 'EICAR'},
    }


class SearchIocWithArtifactsCliTest(TestCase):
    """``search ioc <ip|domain|ttp|imphash> <value> --with-artifacts``.

    autospec makes every call a signature check against the installed SDK, so
    against an SDK below the floor (no ``with_artifacts`` keyword) these fail at
    the mock. The rows are real ``Metadata`` resources: ``output.ioc`` would
    KeyError on them, so the formatter choice is what is under test."""

    def setUp(self):
        self.cli = CliRunner()

    def _run(self, *cmd, fmt='text'):
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY,
             '--output-format', fmt] + list(cmd),
            catch_exceptions=False,
        )

    def _patched(self, rows):
        return mock.patch('polyswarm_api.api.PolyswarmAPI.search_by_ioc',
                          autospec=True, return_value=iter(rows))

    def test_text_renders_the_metadata_block(self):
        row = resources.Metadata(_ioc_artifact_row())
        with self._patched([row]) as search_by_ioc:
            result = self._run('search', 'ioc', 'ip', '9.9.9.9', '--with-artifacts')
        assert result.exit_code == 0, result.output
        search_by_ioc.assert_called_once_with(mock.ANY, ip='9.9.9.9', with_artifacts=True)
        assert 'Metadata' in result.output
        assert 'Artifact id: 31542742786663251' in result.output
        assert f'SHA256: {_FOUND_HASH}' in result.output
        assert 'Malicious: 1' in result.output

    def test_json_renders_the_row(self):
        row = resources.Metadata(_ioc_artifact_row())
        with self._patched([row]):
            result = self._run('search', 'ioc', 'imphash', 'a' * 32, '--with-artifacts',
                               fmt='json')
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == _ioc_artifact_row()

    def test_hash_output_formats_print_the_matching_hash(self):
        row_json = _ioc_artifact_row()
        for fmt in ('sha256', 'sha1', 'md5'):
            with self.subTest(fmt=fmt):
                with self._patched([resources.Metadata(row_json)]):
                    result = self._run('search', 'ioc', 'domain', 'evil.test',
                                       '--with-artifacts', fmt=fmt)
                assert result.exit_code == 0, result.output
                assert result.output.strip() == row_json['artifact'][fmt]

    def test_without_the_flag_the_call_is_unchanged(self):
        with self._patched([]) as search_by_ioc:
            result = self._run('search', 'ioc', 'ttp', 'T1081')
        assert result.exit_code == 0, result.output
        search_by_ioc.assert_called_once_with(mock.ANY, ttp='T1081')

    def test_the_flag_is_refused_on_a_hash_lookup(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.iocs_by_hash',
                        autospec=True) as iocs_by_hash, self._patched([]) as search_by_ioc:
            result = self.cli.invoke(
                client.polyswarm_cli,
                ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY,
                 'search', 'ioc', 'sha256', _FOUND_HASH, '--with-artifacts'])
        assert result.exit_code == 2, result.output
        assert '--with-artifacts applies only to ip, domain, ttp and imphash' in result.output
        iocs_by_hash.assert_not_called()
        search_by_ioc.assert_not_called()
