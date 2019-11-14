import os

from tests.utils.base_test_case import BaseTestCase

from click.testing import CliRunner

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


from tests.resources.mock_server_responses import resources


BASE_PATH = os.path.dirname(__file__)


class SubmissionTest(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super(SubmissionTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '11111111111111111111111111111111'

    def test_submission_create_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.submit', return_value=[resources.submissions(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=iter([resources.submissions(self)[0]])):
            result = self._run_cli(['--output-format', 'json', '-c', 'gamma',
                                    'lookup', '74ac1097-2477-4566-951a-bf0c2716642e'])
        self._assert_json_result(
            result,
            expected_output=resources.submissions(self)[0].json,
            expected_return_code=0,
        )

    def test_submission_lookup_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=iter([resources.submissions(self)[0]])), \
             patch('polyswarm_api.api.PolyswarmAPI.score', return_value=iter([resources.scores(self)[0]])):
            result = self._run_cli(['--output-format', 'text', '-c', 'gamma',
                                    'lookup', '74ac1097-2477-4566-951a-bf0c2716642e'])
        self._assert_text_result(
            result,
            expected_output=resources.text_submissions()[0],
            expected_return_code=0,
        )

    def test_submission_create_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.submit', return_value=[resources.submissions(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=iter([resources.submissions(self)[0]])):
            result = self._run_cli(['--output-format', 'json', '-c', 'gamma',
                                    'scan', os.path.join(BASE_PATH, 'malicious')])
        self._assert_json_result(
            result,
            expected_output=resources.submissions(self)[0].json,
            expected_return_code=0,
        )

    def test_submission_create_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.submit', return_value=[resources.submissions(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=iter([resources.submissions(self)[0]])), \
             patch('polyswarm_api.api.PolyswarmAPI.score', return_value=iter([resources.scores(self)[0]])):
            result = self._run_cli(['--output-format', 'text', '-c', 'gamma',
                                    'scan', os.path.join(BASE_PATH, 'malicious')])
        self._assert_text_result(
            result,
            expected_output=resources.text_submissions()[0],
            expected_return_code=0,
        )

    def test_submission_rescan_json(self):
        with patch('polyswarm_api.api.PolyswarmAPI.submit', return_value=[resources.submissions(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=iter([resources.submissions(self)[0]])):
            result = self._run_cli(['--output-format', 'json', '-c', 'gamma',
                                    'rescan', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'])
        self._assert_json_result(
            result,
            expected_output=resources.submissions(self)[0].json,
            expected_return_code=0,
        )

    def test_submission_rescan_text(self):
        with patch('polyswarm_api.api.PolyswarmAPI.rescan', return_value=[resources.submissions(self)[0]]), \
             patch('polyswarm_api.api.PolyswarmAPI.lookup', return_value=iter([resources.submissions(self)[0]])), \
             patch('polyswarm_api.api.PolyswarmAPI.score', return_value=iter([resources.scores(self)[0]])):
            result = self._run_cli(['--output-format', 'text', '-c', 'gamma',
                                    'rescan', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'])
        self._assert_text_result(
            result,
            expected_output=resources.text_submissions()[0],
            expected_return_code=0,
        )
