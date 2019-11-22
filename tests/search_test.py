import logging

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from tests.utils.base_test_case import BaseTestCase
from tests.utils import mock_polyswarm_api_results
from polyswarm import error_codes

logger = logging.getLogger(__name__)


class SearchTest(BaseTestCase):

    def test_search_hash_with_json_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search',
                   return_value=[mock_polyswarm_api_results.json_results(self)[0]]):
            result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash_value])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.json_results(self)[0].json,
            expected_return_code=0,
        )

    def test_search_hash_with_text_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search',
                   return_value=[mock_polyswarm_api_results.json_results(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.score',
                   return_value=iter([mock_polyswarm_api_results.scores(self)[0]])):
            result = self._run_cli(['--output-format', 'text', 'search', 'hash', self.test_hash_value])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_results()[0],
            expected_return_code=0,
        )

    def test_search_hash_with_no_results(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search',
                   return_value=[]), \
             patch('polyswarm.utils.logger.error') as mock_logger:
            result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash_value])
        mock_logger.assert_called_with('No results found')
        self._assert_text_result(
            result,
            expected_return_code=error_codes.NO_RESULTS_ERROR,
        )

    def test_search_metadata_with_json_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata',
                   return_value=[mock_polyswarm_api_results.json_results(self)[0]]):
            result = self._run_cli(['--output-format', 'json', 'search', 'metadata',
                                    'hash.sha256:' + self.test_hash_value])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.json_results(self)[0].json,
            expected_return_code=0)

    def test_search_metadata_with_text_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata',
                   return_value=[mock_polyswarm_api_results.json_results(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.score',
                   return_value=iter([mock_polyswarm_api_results.scores(self)[0]])):
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata',
                                    'hash.sha256:' + self.test_hash_value])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_results()[0],
            expected_return_code=0,
        )

    def test_search_metadata_with_query_file(self):
        query_file = self._get_test_resource_file_path('inputs/search_metadata_elastic_query.json')
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata',
                   return_value=[mock_polyswarm_api_results.json_results(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.score',
                   return_value=iter([mock_polyswarm_api_results.scores(self)[0]])):
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata',
                                    '--query-file', query_file])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_results()[0],
            expected_return_code=0)

    def test_search_metadata_with_query_file_and_invalid_json(self):
        query_file = self._get_test_resource_file_path('inputs/search_metadata_invalid_elastic_query.json')
        with patch('polyswarm.search.logger.error') as mock_logger:
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata',
                                    '--query-file', query_file])
        mock_logger.assert_called_with('Failed to parse JSON')
        self._assert_text_result(
            result,
            expected_return_code=0)

    def test_search_metadata_with_no_results(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata',
                   return_value=[]), \
             patch('polyswarm.utils.logger.error') as mock_logger:
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata',
                                    'hash.sha256:' + self.test_hash_value])
        mock_logger.assert_called_with('No results found')
        self._assert_text_result(
            result,
            expected_return_code=error_codes.NO_RESULTS_ERROR,
        )