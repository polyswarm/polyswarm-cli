import os

from tests.utils.base_test_case import BaseTestCase

from click.testing import CliRunner

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from tests.utils import mock_polyswarm_api_results

BASE_PATH = os.path.dirname(__file__)


class HuntResultsTest(BaseTestCase):

    def test_live_hunt_results_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.live_results',
                   return_value=[mock_polyswarm_api_results.live_results(self)[0]]):
            result = self._run_cli(['--output-format', 'json',
                                    'live', 'results', '63433636835291189',
                                    '--since', '9999999'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.live_results(self)[0].json,
            expected_return_code=0,
        )

    def test_historical_hunt_results_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.historical_results',
                   return_value=[mock_polyswarm_api_results.historical_results(self)[0]]):
            result = self._run_cli(['--output-format', 'json',
                                    'historical', 'results', '47190397989086018'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.historical_results(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_results_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.live_results',
                   return_value=[mock_polyswarm_api_results.live_results(self)[0]]):
            result = self._run_cli(['--output-format', 'text',
                                    'live', 'results', '63433636835291189',
                                    '--since', '9999999'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_live_results()[0],
            expected_return_code=0,
        )

    def test_historical_hunt_results_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.historical_results',
                   return_value=[mock_polyswarm_api_results.historical_results(self)[0]]):
            result = self._run_cli(['--output-format', 'text',
                                    'historical', 'results', '47190397989086018'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_hisotrical_results()[0],
            expected_return_code=0,
        )


class LiveHuntTest(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super(LiveHuntTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '11111111111111111111111111111111'

    def test_live_hunt_create_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.live_create',
                   return_value=mock_polyswarm_api_results.hunts(self)[0]):
            result = self._run_cli(['--output-format', 'json',
                                    'live', 'start', self._get_test_resource_file_path('eicar.yara')])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_create_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.live_create',
                   return_value=mock_polyswarm_api_results.hunts(self)[0]):
            result = self._run_cli(['--output-format', 'text',
                                    'live', 'start', self._get_test_resource_file_path('eicar.yara')])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_hunts()[0],
            expected_return_code=0,
        )

    def test_live_hunt_delete_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.live_delete',
                   return_value=mock_polyswarm_api_results.hunts(self)[0]):
            result = self._run_cli(['--output-format', 'json',
                                    'live', 'delete', '61210404295535902'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_delete_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.live_delete',
                   return_value=mock_polyswarm_api_results.hunts(self)[0]):
            result = self._run_cli(['--output-format', 'text',
                                    'live', 'delete', '61210404295535902'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_detele_hunts()[0],
            expected_return_code=0,
        )

    def test_live_hunt_list_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.live_list',
                   return_value=[mock_polyswarm_api_results.hunts(self)[0]]):
            result = self._run_cli(['--output-format', 'json',
                                    'live', 'list'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_list_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.live_list',
                   return_value=[mock_polyswarm_api_results.hunts(self)[0]]):
            result = self._run_cli(['--output-format', 'text',
                                    'live', 'list'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_hunts()[0],
            expected_return_code=0,
        )


class HistoricalHuntTest(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super(HistoricalHuntTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '11111111111111111111111111111111'

    def test_historical_hunt_create_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.historical_create',
                   return_value=mock_polyswarm_api_results.hunts(self)[0]):
            result = self._run_cli(['--output-format', 'json',
                                    'historical', 'start', self._get_test_resource_file_path('eicar.yara')])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_historical_hunt_create_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.historical_create',
                   return_value=mock_polyswarm_api_results.hunts(self)[0]):
            result = self._run_cli(['--output-format', 'text',
                                    'historical', 'start', self._get_test_resource_file_path('eicar.yara')])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_hunts()[0],
            expected_return_code=0,
        )

    def test_historical_hunt_delete_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.historical_delete',
                   return_value=mock_polyswarm_api_results.hunts(self)[0]):
            result = self._run_cli(['--output-format', 'json',
                                    'historical', 'delete', '61210404295535902'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_historical_hunt_delete_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.historical_delete',
                   return_value=mock_polyswarm_api_results.hunts(self)[0]):
            result = self._run_cli(['--output-format', 'text',
                                    'historical', 'delete', '61210404295535902'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_detele_hunts()[0],
            expected_return_code=0,
        )

    def test_historical_hunt_list_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.historical_list',
                   return_value=[mock_polyswarm_api_results.hunts(self)[0]]):
            result = self._run_cli(['--output-format', 'json',
                                    'historical', 'list'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_historical_hunt_list_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.historical_list',
                   return_value=[mock_polyswarm_api_results.hunts(self)[0]]):
            result = self._run_cli(['--output-format', 'text',
                                    'historical', 'list'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_hunts()[0],
            expected_return_code=0,
        )
