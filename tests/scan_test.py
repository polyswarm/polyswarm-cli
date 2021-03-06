import os

from tests.utils.base_test_case import BaseTestCase

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from tests.utils import mock_polyswarm_api_results

BASE_PATH = os.path.dirname(__file__)


class SubmissionTest(BaseTestCase):

    def test_submission_lookup_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.submit', return_value=mock_polyswarm_api_results.instances(self)[0]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=mock_polyswarm_api_results.instances(self)[0]):
            result = self._run_cli(['--output-format', 'json', '-c', 'gamma',
                                    'lookup', '49091542211453596'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    def test_submission_lookup_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=mock_polyswarm_api_results.instances(self)[0]):
            result = self._run_cli(['--output-format', 'text', '-c', 'gamma',
                                    'lookup', '49091542211453596'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_instances()[0],
            expected_return_code=0,
        )

    def test_submission_create_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.submit', return_value=mock_polyswarm_api_results.instances(self)[0]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=mock_polyswarm_api_results.instances(self)[0]):
            result = self._run_cli(['--output-format', 'json', '-c', 'gamma',
                                    'scan', 'file', self._get_test_resource_file_path('malicious')])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    def test_submission_create_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.submit', return_value=mock_polyswarm_api_results.instances(self)[0]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=mock_polyswarm_api_results.instances(self)[0]):
            result = self._run_cli(['--output-format', 'text', '-c', 'gamma',
                                    'scan', 'file', self._get_test_resource_file_path('malicious')])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_instances()[0],
            expected_return_code=0,
        )

    def test_submission_rescan_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.rescan', return_value=mock_polyswarm_api_results.instances(self)[0]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=mock_polyswarm_api_results.instances(self)[0]):
            result = self._run_cli(['--output-format', 'json', '-c', 'gamma',
                                    'rescan', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    def test_submission_rescan_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.rescan', return_value=mock_polyswarm_api_results.instances(self)[0]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=mock_polyswarm_api_results.instances(self)[0]):
            result = self._run_cli(['--output-format', 'text', '-c', 'gamma',
                                    'rescan', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_instances()[0],
            expected_return_code=0,
        )

    def test_submission_rescan_id_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.rescan_id', return_value=mock_polyswarm_api_results.instances(self)[0]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=mock_polyswarm_api_results.instances(self)[0]):
            result = self._run_cli(['--output-format', 'json', '-c', 'gamma',
                                    'rescan-id', '11611818710765483'])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    def test_submission_rescan_id_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.rescan_id', return_value=mock_polyswarm_api_results.instances(self)[0]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=mock_polyswarm_api_results.instances(self)[0]):
            result = self._run_cli(['--output-format', 'text', '-c', 'gamma',
                                    'rescan-id', '11611818710765483'])
        self._assert_text_result(
            result,
            expected_output=mock_polyswarm_api_results.text_instances()[0],
            expected_return_code=0,
        )
