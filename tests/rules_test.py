import os

from tests.utils.base_test_case import BaseTestCase

from click.testing import CliRunner

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from tests.utils import mock_polyswarm_api_results

BASE_PATH = os.path.dirname(__file__)


class RulesetTest(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super(RulesetTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '11111111111111111111111111111111'

    def test_ruleset_create_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.ruleset_create',
                   return_value=mock_polyswarm_api_results.ruleset(self)[0]):
            result = self._run_cli(['--output-format', 'json',
                                    'rules', 'create', 'test', self._get_test_resource_file_path('eicar.yara')])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.ruleset(self)[0].json,
            expected_return_code=0,
        )

    def test_ruleset_get_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.ruleset_get',
                   return_value=mock_polyswarm_api_results.ruleset(self)[0]):
            result = self._run_cli(['--output-format', 'json',
                                    'rules', 'view', '67713199207380968'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.ruleset(self)[0].json,
            expected_return_code=0,
        )

    def test_ruleset_update_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.ruleset_update',
                   return_value=mock_polyswarm_api_results.ruleset(self, name='test2')[0]):
            result = self._run_cli(['--output-format', 'json',
                                    'rules', 'update', '67713199207380968', '--name', 'test2'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.ruleset(self, name='test2')[0].json,
            expected_return_code=0,
        )

    def test_ruleset_delete_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.ruleset_delete',
                   return_value=mock_polyswarm_api_results.ruleset(self)[0]):
            result = self._run_cli(['--output-format', 'json',
                                    'rules', 'delete', '67713199207380968'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.ruleset(self)[0].json,
            expected_return_code=0,
        )

    def test_ruleset_list_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.ruleset_list',
                   return_value=[mock_polyswarm_api_results.ruleset(self)[0]]):
            result = self._run_cli(['--output-format', 'json',
                                    'rules', 'list'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.ruleset(self)[0].json,
            expected_return_code=0,
        )
