import logging
import os

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from tests.utils.base_test_case import BaseTestCase
from tests.utils import mock_polyswarm_api_results
from tests.utils import file_utils
from polyswarm import error_codes

logger = logging.getLogger(__name__)


class DownloadTest(BaseTestCase):

    def test_download(self):
        with file_utils.temp_dir(dict(malicious=self.test_eicar)) as (path, files):
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

    def test_download_no_results(self):
        with file_utils.temp_dir(dict(malicious=self.test_eicar)) as (path, files):
            with patch('polyswarm_api.api.PolyswarmAPI.download',
                       return_value=[]), \
                 patch('polyswarm.utils.logger.error') as mock_logger:
                result = self._run_cli(['download', self.test_hash_value, path])
                mock_logger.assert_called_with('No results found')
                self._assert_text_result(
                    result,
                    expected_return_code=error_codes.NO_RESULTS_ERROR,
                )

    def test_cat(self):
        with patch('polyswarm_api.http.PolyswarmHTTP.request',
                   return_value=mock_polyswarm_api_results.cat_request(self.test_eicar)):
            result = self._run_cli(['cat', self.test_hash_value])
            self._assert_text_result(
                result,
                expected_output=self.test_eicar.decode(),
                expected_return_code=0,
            )

    def test_stream(self):
        with file_utils.temp_dir(dict(malicious=self.test_eicar)) as (path, files):
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

    def test_stream_no_results(self):
        with file_utils.temp_dir(dict(malicious=self.test_eicar)) as (path, files):
            with patch('polyswarm_api.api.PolyswarmAPI.stream',
                       return_value=[]), \
                 patch('polyswarm.utils.logger.error') as mock_logger:
                result = self._run_cli(['stream', path])
                mock_logger.assert_called_with('No results found')
                self._assert_text_result(
                    result,
                    expected_return_code=error_codes.NO_RESULTS_ERROR,
                )