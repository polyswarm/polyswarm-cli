import logging

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from polyswarm_api import exceptions as api_exceptions

from tests.utils.base_test_case import BaseTestCase
from tests.utils import mock_polyswarm_api_results

logger = logging.getLogger(__name__)


class SearchTest(BaseTestCase):

    def test_search_hash_with_json_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search',
                   return_value=[mock_polyswarm_api_results.instances(self)[0]]):
            result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash_value])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    def test_search_hash_with_text_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search',
                   return_value=[mock_polyswarm_api_results.instances(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.score',
                   return_value=mock_polyswarm_api_results.scores(self)[0]):
            result = self._run_cli(['--output-format', 'text', 'search', 'hash', self.test_hash_value])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_instances()[0],
            expected_return_code=0,
        )

    def test_search_hash_with_no_results(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search', side_effect=api_exceptions.NoResultsException(None)):
            result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash_value])
        self._assert_text_result(
            result,
            expected_return_code=2,
        )

    def test_search_metadata_with_json_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata',
                   return_value=[mock_polyswarm_api_results.instances(self)[0]]):
            result = self._run_cli(['--output-format', 'json', 'search', 'metadata',
                                    'hash.sha256:' + self.test_hash_value])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0)

    def test_search_metadata_with_text_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata',
                   return_value=[mock_polyswarm_api_results.instances(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.score',
                   return_value=mock_polyswarm_api_results.scores(self)[0]):
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata',
                                    'hash.sha256:' + self.test_hash_value])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_instances()[0],
            expected_return_code=0,
        )

    def test_search_metadata_with_no_results(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata',
                   side_effect=api_exceptions.NoResultsException(None)):
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata',
                                    'hash.sha256:' + self.test_hash_value])
        self._assert_text_result(
            result,
            expected_return_code=2,
        )
