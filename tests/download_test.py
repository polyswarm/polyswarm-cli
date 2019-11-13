import logging
import tempfile
import shutil
import os
from contextlib import contextmanager
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from click.testing import CliRunner

from tests.utils.base_test_case import BaseTestCase
from tests.resources.mock_server_responses import resources

logger = logging.getLogger(__name__)


@contextmanager
def TemporaryDirectory():
    """The day we drop python 2.7 support we can use python 3 version of this"""
    name = tempfile.mkdtemp()
    try:
        yield name
    finally:
        shutil.rmtree(name)


@contextmanager
def temp_dir(files_dict):
    with TemporaryDirectory() as tmp_dir:
        files = []
        for file_name, file_content in files_dict.items():
            file_path = os.path.join(tmp_dir, file_name)
            mode = 'w' if isinstance(file_content, str) else 'wb'
            with open(file_path, mode=mode) as f:
                f.write(file_content)
            files.append(file_path)
        yield tmp_dir, files


class DownloadTest(BaseTestCase):
    def __init__(self, *args, **kwargs):
        super(DownloadTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '11111111111111111111111111111111'
        self.test_hash = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
        self.eicar = b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.api_url = 'http://localhost:9696/v2/consumer'

    def test_download(self):
        with temp_dir(dict(malicious=self.eicar)) as (path, files):
            with patch('polyswarm_api.api.PolyswarmAPI.download', return_value=[resources.local_artifacts(files)[0]]):
                result = self._run_cli(['download', self.test_hash, path])
                self._assert_text_result(
                    result,
                    expected_output=resources.text_local_artifacts(path)[0],
                    expected_return_code=0,
                )

    def test_cat(self):
        with patch('polyswarm_api.http.PolyswarmHTTP.request', return_value=resources.cat_request(self.eicar)):
            result = self._run_cli(['cat', self.test_hash])
            self._assert_text_result(
                result,
                expected_output=self.eicar.decode(),
                expected_return_code=0,
            )

    def test_stream(self):
        with temp_dir(dict(malicious=self.eicar)) as (path, files):
            with patch('polyswarm_api.api.PolyswarmAPI.stream', return_value=[resources.local_artifacts(files)[0]]):
                result = self._run_cli(['stream', path])
                self._assert_text_result(
                    result,
                    expected_output=resources.text_local_artifacts(path)[0],
                    expected_return_code=0,
                )