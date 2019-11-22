import logging
import os

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

from tests.utils.base_test_case import BaseTestCase
from tests.utils import mock_polyswarm_api_results
from tests.utils import file_utils

logger = logging.getLogger(__name__)


class DownloadTest(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super(DownloadTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '11111111111111111111111111111111'
        self.eicar = b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.api_url = 'http://localhost:9696/v2/consumer'

    def test_download(self):
        with file_utils.temp_dir(dict(malicious=self.eicar)) as (path, files):
            with patch('polyswarm_api.api.PolyswarmAPI.download',
                       return_value=[mock_polyswarm_api_results.local_artifacts(self.test_hash_value, path)[0]]):
                result = self._run_cli(['download', self.test_hash_value, path])
                self._assert_text_result(
                    result,
                    expected_output=mock_polyswarm_api_results.text_local_artifacts(
                        self.test_hash_value,
                        os.path.join(path, self.test_hash_value))[0],
                    expected_return_code=0,
                )

    def test_cat(self):
        with patch('polyswarm_api.http.PolyswarmHTTP.request',
                   return_value=mock_polyswarm_api_results.cat_request(self.eicar)):
            result = self._run_cli(['cat', self.test_hash_value])
            self._assert_text_result(
                result,
                expected_output=self.eicar.decode(),
                expected_return_code=0,
            )

    def test_stream(self):
        with file_utils.temp_dir(dict(malicious=self.eicar)) as (path, files):
            with patch('polyswarm_api.api.PolyswarmAPI.stream',
                       return_value=[mock_polyswarm_api_results.local_artifacts(self.test_hash_value, path)[0]]):
                result = self._run_cli(['stream', path])

                self._assert_text_result(
                    result,
                    expected_output=mock_polyswarm_api_results.text_local_artifacts(
                        self.test_hash_value,
                        os.path.join(path, self.test_hash_value))[0],
                    expected_return_code=0,
                )