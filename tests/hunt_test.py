from tests.utils.base_test_case import BaseTestCase

from click.testing import CliRunner

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


from tests.resources.mock_server_responses import resources


class HuntTest(BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(HuntTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '11111111111111111111111111111111'

    def test_live_hunt_results_json(self):
        # with patch('polyswarm_api.api.PolyswarmAPI.search', return_value=[resources.instances()[0]]):
        result = self._run_cli(['--output-format', 'json',
                                'live', 'results', '63433636835291189',
                                '--since', '99999999999999'])
        self._assert_json_result(
            result,
            expected_output=resources.instances()[0].json,
            expected_return_code=0,
        )
