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
        # with patch('polyswarm_api.api.PolyswarmAPI.historical_create', return_value=resources.hunts()[0]):
        result = self._run_cli(['--output-format', 'json', '-c', 'gamma',
                                'scan', os.path.join(BASE_PATH, 'malicious')])
        self._assert_json_result(
            result,
            expected_output=resources.hunts()[0].json,
            expected_return_code=0,
        )

    def test_submission_create_text(self):
        # with patch('polyswarm_api.api.PolyswarmAPI.historical_create', return_value=resources.hunts()[0]):
        result = self._run_cli(['--output-format', 'text', '-c', 'gamma',
                                'scan', os.path.join(BASE_PATH, 'malicious')])
        self._assert_json_result(
            result,
            expected_output=resources.hunts()[0].json,
            expected_return_code=0,
        )
