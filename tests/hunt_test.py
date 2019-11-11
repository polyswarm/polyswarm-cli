import pytest

from tests.utils.base_test_case import BaseTestCase

from click.testing import CliRunner

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


from tests.resources.mock_server_responses import resources


class SearchTest(BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(SearchTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '11111111111111111111111111111111'
        self.test_hash = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
        self.invalid_hash = 'definitely-not-a-valid-hash'
        self.test_query = '_exists_:lief.libraries'
        self.test_elastic_query = '{"query": {"query_string": {"query": "%s"}}}' % self.test_query
        self.test_invalid_query = 'definitely-not-json'

    def test_search_hash_with_json_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search', return_value=[resources.instances()[0]]):
            result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash])
        self._assert_json_result(
            result,
            expected_output=resources.instances()[0].json,
            expected_return_code=0,
        )

    def test_search_hash_with_text_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search', return_value=[resources.instances()[0]]):
            result = self._run_cli(['--output-format', 'text', 'search', 'hash', self.test_hash])
        self._assert_text_result(
            result,
            expected_output=resources.text_instances()[0],
            expected_return_code=0,
        )

    def test_search_metadata_with_json_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata', return_value=[resources.instances()[0]]):
            result = self._run_cli(['--output-format', 'json', 'search', 'metadata', 'hash.sha256:' + self.test_hash])
        self._assert_json_result(
            result,
            expected_output=resources.instances()[0].json,
            expected_return_code=0)

    def test_search_metadata_with_text_output(self):
        with patch('polyswarm_api.api.PolyswarmAPI.search_by_metadata', return_value=[resources.instances()[0]]):
            result = self._run_cli(['--output-format', 'text', 'search', 'metadata', 'hash.sha256:' + self.test_hash])
        self._assert_text_result(
            result,
            expected_output=resources.text_instances()[0],
            expected_return_code=0,
        )
