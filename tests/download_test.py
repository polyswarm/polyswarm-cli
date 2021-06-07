import logging
import os

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from tests.utils.base_test_case import BaseTestCase
from tests.utils import mock_polyswarm_api_results
from tests.utils import file_utils

logger = logging.getLogger(__name__)


class DownloadTest(BaseTestCase):

    def test_download(self):
        with file_utils.temp_dir({self.test_hash_value: self.test_eicar}) as (path, files):
            with patch('polyswarm_api.api.PolyswarmAPI.download',
                       return_value=mock_polyswarm_api_results.local_artifacts(self, path, files)[0]):
                result = self._run_cli(['download', '-d', path, self.test_hash_value])
                self._assert_text_result(
                    result,
                    expected_result=mock_polyswarm_api_results.text_local_artifacts(
                        self.test_hash_value,
                        os.path.join(path, self.test_hash_value))[0],
                    expected_return_code=0,
                )

    def test_cat(self):
        with patch('polyswarm_api.core.PolyswarmSession.request',
                   return_value=mock_polyswarm_api_results.cat_request(self.test_eicar)):
            result = self._run_cli(['cat', self.test_hash_value])
            self._assert_text_result(
                result,
                expected_result=self.test_eicar.decode(),
                expected_return_code=0,
            )

    def test_stream(self):
        with file_utils.temp_dir({self.test_hash_value: self.test_eicar}) as (path, files):
            with patch('polyswarm_api.api.PolyswarmAPI.stream',
                       return_value=[mock_polyswarm_api_results.artifact_archives(self)[0]]),\
                 patch('polyswarm_api.api.PolyswarmAPI.download_archive',
                       return_value=mock_polyswarm_api_results.local_artifacts(self, path, files)[0]):
                result = self._run_cli(['stream', path])

                self._assert_text_result(
                    result,
                    expected_result=mock_polyswarm_api_results.text_local_artifacts(
                        self.test_hash_value,
                        os.path.join(path, self.test_hash_value))[0],
                    expected_return_code=0,
                )
