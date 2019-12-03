import requests_mock
import io
import os

from tests.utils.base_test_case import BaseTestCase
from tests.utils import mock_polyswarm_api_results
from tests.utils import file_utils

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@requests_mock.Mocker()
class IntegrationTest(BaseTestCase):
    """
        These tests mock the resource end-point, thus also sanity testing polyswarm-api.
    """

    def __init__(self, *args, **kwargs):
        super(IntegrationTest, self).__init__(*args, **kwargs)
        self.mock_search_response_page1 = self._create_response([mock_polyswarm_api_results.instances(self)[0].json],
                                                                offset=0, limit=1)
        self.mock_search_response_page2 = self._create_response([], offset=1, limit=1)

        self.mock_submission_response = \
            self._create_response(mock_polyswarm_api_results.instances(self)[0].json)

        self.mock_hunt_live_results_response_page1 = \
            self._create_response([mock_polyswarm_api_results.live_results(self)[0].json], offset=0, limit=1)
        self.mock_hunt_live_results_response_page2 = self._create_response([], offset=1, limit=1)

        self.mock_hunt_historical_results_response_page1 = \
            self._create_response([mock_polyswarm_api_results.historical_results(self)[0].json], offset=0, limit=1)
        self.mock_hunt_historical_results_response_page2 = self._create_response([], offset=1, limit=1)

        self.mock_hunt_response = self._create_response(mock_polyswarm_api_results.hunts(self)[0].json)
        self.mock_hunt_response_page1 = self._create_response([mock_polyswarm_api_results.hunts(self)[0].json],
                                                              offset=0, limit=1)
        self.mock_hunt_response_page2 = self._create_response([], offset=1, limit=1)

        self.mock_stream_response_page1 = self._create_response(
            [mock_polyswarm_api_results.stream_results(self.test_s3_file_url)[0]],
            offset=0, limit=1)
        self.mock_stream_response_page2 = self._create_response([], offset=1, limit=1)

    def test_search_hash(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_search_hash_request(self.test_hash_value),
                                      response=self.mock_search_response_page1)
        self._setup_mock_api_response(mock_server,
                                      request=self._create_search_hash_request(self.test_hash_value, offset=1, limit=1),
                                      response=self.mock_search_response_page2)

        result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash_value])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0)

    def test_search_metadata(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_search_metadata_request(self.test_query),
                                      response=self.mock_search_response_page1)
        self._setup_mock_api_response(mock_server,
                                      request=self._create_search_metadata_request(self.test_query, offset=1, limit=1),
                                      response=self.mock_search_response_page2)

        result = self._run_cli(['--output-format', 'json', 'search', 'metadata', self.test_query])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0)

    def test_scan_submission_lookup(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_scan_submission_lookup_request(self.test_submission_uuid),
                                      response=self.mock_submission_response)

        result = self._run_cli(['--output-format', 'json', '-c', 'lima', 'lookup', self.test_submission_uuid])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    def test_scan_submission_create(self, mock_server):
        malicious_file = self._get_test_resource_file_path('malicious')
        self._setup_mock_api_response(mock_server,
                                      request=self._create_scan_submission_lookup_request(self.test_submission_uuid),
                                      response=self.mock_submission_response)

        self._setup_mock_api_response(mock_server,
                                      request=self._create_scan_submission_submit_request(malicious_file),
                                      response=self.mock_submission_response)

        result = self._run_cli(['--output-format', 'json', '-c', 'lima', 'scan', malicious_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    def test_scan_submission_rescan(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_scan_submission_rescan_request(self.test_hash_value),
                                      response=self.mock_submission_response)
        self._setup_mock_api_response(mock_server,
                                      request=self._create_scan_submission_lookup_request(self.test_submission_uuid),
                                      response=self.mock_submission_response)

        result = self._run_cli(['--output-format', 'json', '-c', 'lima', 'rescan', self.test_hash_value])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_results(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_live_results_request(self.test_hunt_id,
                                                                                     self.test_since),
                                      response=self.mock_hunt_live_results_response_page1)
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_live_results_request(self.test_hunt_id, self.test_since,
                                                                                     offset=1, limit=1),
                                      response=self.mock_hunt_live_results_response_page2)

        result = self._run_cli(['--output-format', 'json', 'live', 'results', self.test_hunt_id,
                                '--since', self.test_since])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.live_results(self)[0].json,
            expected_return_code=0,
        )

    def test_historical_hunt_results(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_historical_results_request(self.test_hunt_id),
                                      response=self.mock_hunt_historical_results_response_page1)
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_historical_results_request(self.test_hunt_id,
                                                                                           offset=1, limit=1),
                                      response=self.mock_hunt_historical_results_response_page2)

        result = self._run_cli(['--output-format', 'json', 'historical', 'results', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.historical_results(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_start(self, mock_server):
        yara_file = self._get_test_resource_file_path('eicar.yara')
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_live_start_request(yara_file),
                                      response=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'live', 'start', yara_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_start_with_invalid_yara_file(self, mock_server):
        broken_yara_file = self._get_test_resource_file_path('broken.yara')
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_live_start_request(broken_yara_file),
                                      response=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'live', 'start', broken_yara_file])

        self._assert_text_result(
            result,
            expected_output='"Malformed yara file: line 1: syntax error, unexpected identifier"',
            expected_return_code=2,
        )

    def test_historical_hunt_start(self, mock_server):
        yara_file = self._get_test_resource_file_path('eicar.yara')
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_historical_start_request(yara_file),
                                      response=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'historical', 'start', yara_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_delete(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_live_delete_request(self.test_hunt_id),
                                      response=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'live', 'delete', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_historical_hunt_delete(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_historical_delete_request(self.test_hunt_id),
                                      response=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'historical', 'delete', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_live_hunt_list(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_live_list_request(),
                                      response=self.mock_hunt_response_page1)
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_live_list_request(offset=1, limit=1),
                                      response=self.mock_hunt_response_page2)

        result = self._run_cli(['--output-format', 'json', 'live', 'list'])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_historical_hunt_list(self, mock_server):
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_historical_list_request(),
                                      response=self.mock_hunt_response_page1)
        self._setup_mock_api_response(mock_server,
                                      request=self._create_hunt_historical_list_request(offset=1, limit=1),
                                      response=self.mock_hunt_response_page2)

        result = self._run_cli(['--output-format', 'json', 'historical', 'list'])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    def test_download(self, mock_server):
        with file_utils.temp_dir(dict(malicious=self.test_eicar)) as (path, files):
            self._setup_mock_api_download(mock_server,
                                          request=self._create_download_request(self.test_hash_value, files[0]),
                                          download_file=io.BytesIO(self.test_eicar))

            result = self._run_cli(['download', self.test_hash_value, path])

            self._assert_text_result(
                result,
                expected_output=mock_polyswarm_api_results.text_local_artifacts(
                    self.test_hash_value,
                    os.path.join(path, self.test_hash_value))[0],
                expected_return_code=0,
            )

    def test_download_stream(self, mock_server):
        with file_utils.temp_dir(dict(malicious=self.test_eicar)) as (path, files):
            self._setup_mock_api_response(mock_server,
                                          request=self._create_stream_request(self.test_since),
                                          response=self.mock_stream_response_page1)
            self._setup_mock_url_response(mock_server,
                                          url=self.test_s3_file_url,
                                          response=io.BytesIO(self.test_eicar))
            self._setup_mock_api_response(mock_server,
                                          request=self._create_stream_request(self.test_since, offset=1, limit=1),
                                          response=self.mock_stream_response_page2)

            result = self._run_cli(['stream', '--since', self.test_since, path])

            self._assert_text_result(
                result,
                expected_output=mock_polyswarm_api_results.text_local_artifacts(
                    self.test_hash_value,
                    os.path.join(path, self.test_hash_value))[0],
                expected_return_code=0,
            )

    def test_download_cat(self, mock_server):
        with file_utils.temp_dir(dict(malicious=self.test_eicar)) as (path, files):
            self._setup_mock_api_download(mock_server,
                                          request=self._create_download_request(self.test_hash_value, files[0]),
                                          download_file=io.BytesIO(self.test_eicar))

            result = self._run_cli(['cat', self.test_hash_value])
            self._assert_text_result(
                result,
                expected_output=self.test_eicar.decode(),
                expected_return_code=0,
            )
