from unittest import TestCase
from polyswarm_api.types.hash import to_hash
from polyswarm_api.types.query import MetadataQuery
from .base import BaseTestCase

from click.testing import CliRunner
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

TestCase.maxDiff = None


class ScanTest(BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(ScanTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.bad_hash = 'lmao'
        self.bad_file = '/tmp/never_gonna_give_you_up'
        self.bad_uuid = 'never-gonna-let-you-down'

    def test_rescan_invalid_hash(self):
        commands = ['rescan', self.bad_hash]
        self._do_fail_test([], 'text', None, commands)

    def test_scan_invalid_file(self):
        commands = ['scan', self.bad_file]
        self._do_fail_test([], 'text', None, commands)

    def test_lookup_invalid_uuid(self):
        commands = ['lookup', self.bad_uuid]
        self._do_fail_test([], 'text', None, commands)

    """
    def test_search_with_hash_parameter(self):
        expected_output = self._get_test_text_resource_content('expected_search_hashes_output.txt')
        with patch('polyswarm_api.api.PolyswarmAPI.search') as mock_search_hashes:
            mock_search_hashes.side_effect = self._mock_search_hashes_with_results
            result = self.test_runner.invoke(polyswarm, ['--api-key', self.test_api_key, '--output-format', 'json',
                                                         '--output-file', self.test_captured_output_file,
                                                         'search', 'hash', self.test_hash])
        self.assertEqual(result.exit_code, 0, msg=result.exception)
        output = self._get_file_content(self.test_captured_output_file)
        self.assertEqual(output, expected_output)

    def test_search_with_query_parameter(self):
        expected_output = self._get_test_text_resource_content('expected_cli_search_query_output.txt')
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata') as mock_search_hashes:
            mock_search_hashes.side_effect = self._mock_search_query_with_results
            result = self.test_runner.invoke(polyswarm,
                                             ['-vvv', '--api-key', self.test_api_key, '--output-format', 'json',
                                              '--output-file', self.test_captured_output_file,
                                              'search', 'metadata', self.test_query])

        self.assertEqual(result.exit_code, 0, msg=traceback.format_tb(result.exc_info[2]))
        output = self._get_file_content(self.test_captured_output_file)
        self.assertEqual(output, expected_output)

    @staticmethod
    def _get_test_text_resource_content(resource):
        return resource_string('test.resources', resource).decode('utf-8')

    def _get_test_json_resource_content(self, resource):
        return json.loads(self._get_test_text_resource_content(resource))

    def _mock_search_hashes_with_results(self, hashes, with_instances=False, with_metadata=True):
        success_json = self._get_test_json_resource_content('expected_search_success_results_hash.json')

        self.adapter.register_uri('GET', 'mock://api.polyswarm.network/v1/search', json=success_json)

        def result_generator():
            yield result.SearchResult([to_hash(hashes)], self.session.get('mock://api.polyswarm.network/v1/search'))
        return result_generator()

    def _mock_search_query_with_results(self, query, with_instances=False, with_metadata=True, raw=True):
        success_json = self._get_test_json_resource_content('expected_search_success_results.json')
        self.adapter.register_uri('GET', 'mock://api.polyswarm.network/v1/search', json=success_json)

        def result_generator():
            yield result.SearchResult(query, self.session.get('mock://api.polyswarm.network/v1/search'))
        return result_generator()

"""
