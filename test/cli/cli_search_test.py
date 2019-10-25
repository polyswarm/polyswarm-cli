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


class SearchTest(BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(SearchTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '963da5a463b0ab61fe0f96f82846490d'
        self.bad_hash = 'lmao'
        self.test_hash = '08666dae57ea6a8ef21cfa38cf41db395e8c39c61b1f281cb6927b2bca07fb1d'
        self.test_query = "_exists_:lief.libraries"

    def test_search_with_hash_parameter(self):
        commands = ['search', 'hash', self.test_hash]
        reqs = [
            (self.request_generator.search_hash(to_hash(self.test_hash)),
             self._get_test_text_resource_content('expected_search_success_results_hash.json')),
        ]
        self._do_success_test(reqs, 'json', 'expected_search_hashes_output.txt', commands)

    def test_search_hash_no_result(self):
        commands = ['search', 'hash', self.test_hash]
        reqs = [
            (self.request_generator.search_hash(to_hash(self.test_hash)),
             self._get_test_text_resource_content('expected_search_query_not_found_results.json')),
        ]
        self._do_fail_test(reqs, 'json', None, commands)

    def test_search_with_query_parameter(self):
        commands = ['search', 'metadata', self.test_query]
        reqs = [
            (self.request_generator.search_metadata(MetadataQuery(self.test_query)),
             self._get_test_text_resource_content('expected_search_success_results.json')),
        ]
        self._do_success_test(reqs, 'json', 'expected_cli_search_query_output.txt', commands)

    def test_search_query_no_result(self):
        commands = ['search', 'metadata', self.test_query]
        reqs = [
            (self.request_generator.search_metadata(MetadataQuery(self.test_query)),
             self._get_test_text_resource_content('expected_search_query_not_found_results.json')),
        ]
        self._do_fail_test(reqs, 'json', None, commands)

    def test_search_invalid_hash(self):
        commands = ['search', 'hash', self.bad_hash]
        self._do_fail_test([], 'text', 'expected_cli_search_bad_hash.txt', commands)
