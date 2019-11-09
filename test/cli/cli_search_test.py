from test.utils.base_test_case import BaseTestCase

from click.testing import CliRunner

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import requests_mock


@requests_mock.Mocker()
class SearchTest(BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(SearchTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '963da5a463b0ab61fe0f96f82846490d'
        self.test_hash = '08666dae57ea6a8ef21cfa38cf41db395e8c39c61b1f281cb6927b2bca07fb1d'
        self.invalid_hash = 'definitely-not-a-valid-hash'
        self.test_query = '_exists_:lief.libraries'
        self.test_elastic_query = '{"query": {"query_string": {"query": "%s"}}}' % self.test_query
        self.test_invalid_query = 'definitely-not-json'

    def test_search_hash_with_json_output(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_hash_request(self.test_hash),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_single_result.json'))
        result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash])
        self._assert_json_result(
            result,
            expected_output=self._get_test_json_resource_content('expectations/expected_search_hash_output.json'),
            expected_return_code=0)

    def test_search_hash_with_text_output(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_hash_request(self.test_hash),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_single_result.json'))
        result = self._run_cli(['--output-format', 'text', 'search', 'hash', self.test_hash])
        self._assert_text_result(
            result,
            expected_output=self._get_test_text_resource_content('expectations/expected_search_hash_output.txt'),
            expected_return_code=0)

    def test_search_hash_with_no_result(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_hash_request(self.test_hash),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_not_found_result.json'))
        result = self._run_cli(['--output-format', 'text', 'search', 'hash', self.test_hash])
        self._assert_text_result(
            result,
            expected_output='Did not find any files matching search: sha256=%s.' % self.test_hash,
            expected_return_code=1)

    def test_search_hash_with_invalid_hash(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_hash_request(self.test_hash),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_single_result.json'))
        result = self._run_cli(['--output-format', 'text', 'search', 'hash', self.invalid_hash])
        self._assert_text_result(
            result,
            expected_output=self._get_test_text_resource_content(
                'expectations/expected_search_hash_with_invalid_hash_output.txt'),
            expected_return_code=2)

    def test_search_metadata_with_text_output(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_metadata_request(self.test_query),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_results.json'))
        result = self._run_cli(['--output-format', 'text', 'search', 'metadata', self.test_query])
        self._assert_text_result(
            result,
            expected_output=self._get_test_text_resource_content('expectations/expected_search_metadata_output.txt'),
            expected_return_code=0)

    def test_search_metadata_with_json_output(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_metadata_request(self.test_query),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_results.json'))
        result = self._run_cli(['--output-format', 'json', 'search', 'metadata', self.test_query])
        self._assert_json_result(
            result,
            expected_output=self._get_test_json_resource_content('expectations/expected_search_metadata_output.json'),
            expected_return_code=0)

    def test_search_metadata_without_metadata_and_with_json_output(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_metadata_request(self.test_query, with_metadata=False),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_results_without_metadata.json'))
        result = self._run_cli(['--output-format', 'json', 'search', 'metadata', self.test_query, '--without-metadata'])
        self._assert_json_result(
            result,
            expected_output=self._get_test_json_resource_content(
                'expectations/expected_search_without_metadata_output.json'),
            expected_return_code=0)

    def test_search_metadata_with_no_result(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_metadata_request(self.test_query),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_not_found_result.json'))
        result = self._run_cli(['--output-format', 'text', 'search', 'metadata', self.test_query])
        self._assert_text_result(
            result,
            expected_output='Did not find any files matching search: %s.' % self.test_elastic_query,
            expected_return_code=1)

    def test_search_metadata_with_query_file_and_text_output(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_metadata_request(self.test_query),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_results.json'))
        query_file = self._get_test_resource_file_path('search_metadata_elastic_query.json')
        with patch('polyswarm_api.log.logger.error', side_effect=self.mock_logger):
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata',
                                    '--query-file', query_file])
        self._assert_text_result(
            result,
            expected_output=self._get_test_text_resource_content('expectations/expected_search_metadata_output.txt'),
            expected_return_code=0)

    def test_search_metadata_with_query_file_and_json_output(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_metadata_request(self.test_query),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_results.json'))
        query_file = self._get_test_resource_file_path('search_metadata_elastic_query.json')
        with patch('polyswarm_api.log.logger.error', side_effect=self.mock_logger):
            result = self._run_cli(['--output-format', 'json', 'search', 'metadata',
                                    '--query-file', query_file])
        self._assert_json_result(
            result,
            expected_output=self._get_test_json_resource_content('expectations/expected_search_metadata_output.json'),
            expected_return_code=0)

    def test_search_metadata_with_invalid_json(self, mock_server):
        self._setup_mock_response(mock_server,
                                  request=self._create_metadata_request(self.test_query),
                                  response=self._get_test_text_resource_content(
                                      'responses/search_success_results.json'))
        query_file = self._get_test_resource_file_path('search_metadata_invalid_elastic_query.json')
        with patch('polyswarm_api.log.logger.error', side_effect=self.mock_logger):
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata',
                                    '--query-file', query_file])
        self._assert_text_result(
            result,
            expected_output='Failed to parse JSON',
            expected_return_code=0)
