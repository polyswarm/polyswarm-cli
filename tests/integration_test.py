import io
import os

import requests
import responses

from tests.utils.base_test_case import BaseTestCase
from tests.utils import mock_polyswarm_api_results
from tests.utils import file_utils


class IntegrationTest(BaseTestCase):
    """
        These tests mock the resource end-point, thus also sanity testing polyswarm-api.
    """

    @responses.activate
    def __init__(self, *args, **kwargs):
        super(IntegrationTest, self).__init__(*args, **kwargs)
        self.mock_search_response_page1 = self._create_response([mock_polyswarm_api_results.instances(self)[0].json],
                                                                offset=1, limit=1, has_more=False)

        self.mock_metadata_search_response = self._create_response([mock_polyswarm_api_results.metadata(self)[0].json],
                                                                   offset=1, limit=1, has_more=False)

        self.mock_submission_response = \
            self._create_response(mock_polyswarm_api_results.instances(self)[0].json)

        self.mock_hunt_live_results_response_page1 = \
            self._create_response([mock_polyswarm_api_results.live_results(self)[0].json], offset=1, limit=1, has_more=False)

        self.mock_hunt_historical_results_response_page1 = \
            self._create_response([mock_polyswarm_api_results.historical_results(self)[0].json], offset=1, limit=1, has_more=False)

        self.mock_hunt_response = self._create_response(mock_polyswarm_api_results.hunts(self)[0].json)
        self.mock_hunt_response_page1 = self._create_response([mock_polyswarm_api_results.hunts(self)[0].json],
                                                              offset=1, limit=1, has_more=False)

        self.mock_stream_response_page1 = self._create_response(
            [mock_polyswarm_api_results.stream_results(self.test_s3_file_url)[0]],
            offset=1, limit=1, has_more=False)

    @responses.activate
    def test_search_hash(self):
        request = self._create_search_hash_request(self.test_hash_value)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_search_response_page1)
        result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash_value])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0)

    @responses.activate
    def test_search_metadata(self):
        request = self._create_search_metadata_request(self.test_query)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_metadata_search_response)
        result = self._run_cli(['--output-format', 'json', 'search', 'metadata', self.test_query])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.metadata(self)[0].json,
            expected_return_code=0)

    @responses.activate
    def test_scan_submission_lookup(self):
        request = self._create_scan_submission_lookup_request(self.test_submission_uuid)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_submission_response)

        result = self._run_cli(['--output-format', 'json', '-c', self.community, 'lookup', self.test_submission_uuid])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_scan_submission_create(self):
        request = self._create_scan_submission_lookup_request(self.test_submission_uuid)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_submission_response)

        malicious_file = self._get_test_resource_file_path('malicious')
        request = self._create_scan_submission_submit_request(malicious_file)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.POST, url, body=self.mock_submission_response)

        result = self._run_cli(['--output-format', 'json', '-c', self.community, 'scan', 'file', malicious_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_scan_submission_rescan(self):
        request = self._create_scan_submission_rescan_request(self.test_hash_value)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.POST, url, body=self.mock_submission_response)

        request = self._create_scan_submission_lookup_request(self.test_submission_uuid)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_submission_response)

        result = self._run_cli(['--output-format', 'json', '-c', self.community, 'rescan', self.test_hash_value])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_results(self):
        request = self._create_hunt_live_results_request(self.test_hunt_id, self.test_since)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_hunt_live_results_response_page1)

        result = self._run_cli(['--output-format', 'json', 'live', 'results', self.test_hunt_id,
                                '--since', self.test_since])
        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.live_results(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_historical_hunt_results(self):
        request = self._create_hunt_historical_results_request(self.test_hunt_id)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_hunt_historical_results_response_page1)

        result = self._run_cli(['--output-format', 'json', 'historical', 'results', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.historical_results(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_start(self):
        yara_file = self._get_test_resource_file_path('eicar.yara')
        request = self._create_hunt_live_start_request(yara_file)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.POST, url, body=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'live', 'create', yara_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_start_with_invalid_yara_file(self):
        broken_yara_file = self._get_test_resource_file_path('broken.yara')
        request = self._create_hunt_live_start_request(broken_yara_file)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.POST, url, body=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'live', 'create', broken_yara_file])

        self._assert_text_result(
            result,
            expected_output='error [polyswarm.client.polyswarm]: Malformed yara file: line 1: syntax error, unexpected identifier',
            expected_return_code=2,
        )

    @responses.activate
    def test_historical_hunt_start(self):
        yara_file = self._get_test_resource_file_path('eicar.yara')
        request = self._create_hunt_historical_start_request(yara_file)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.POST, url, body=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'historical', 'start', yara_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_delete(self):
        request = self._create_hunt_live_delete_request(self.test_hunt_id)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.DELETE, url, body=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'live', 'delete', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_historical_hunt_delete(self):
        request = self._create_hunt_historical_delete_request(self.test_hunt_id)
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.DELETE, url, body=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'historical', 'delete', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_list(self):
        request = self._create_hunt_live_list_request()
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'live', 'list'])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_historical_hunt_list(self):
        request = self._create_hunt_historical_list_request()
        url = requests.Request(**request.request_parameters).prepare().url
        responses.add(responses.GET, url, body=self.mock_hunt_response_page1)

        result = self._run_cli(['--output-format', 'json', 'historical', 'list'])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_download(self):
        with file_utils.temp_dir({self.test_hash_value: self.test_eicar}) as (path, files):
            request = self._create_download_request(self.test_hash_value)
            request.request_parameters.pop('stream')
            url = requests.Request(**request.request_parameters).prepare().url
            responses.add(responses.GET, url, body=self.test_eicar, stream=True)

            result = self._run_cli(['download', self.test_hash_value, path])

            self._assert_text_result(
                result,
                expected_output=mock_polyswarm_api_results.text_local_artifacts(
                    self.test_hash_value,
                    os.path.join(path, self.test_hash_value))[0],
                expected_return_code=0,
            )

    @responses.activate
    def test_download_stream(self):
        with file_utils.temp_dir({self.test_hash_value: self.test_eicar}) as (path, files):
            request = self._create_stream_request(self.test_since)
            url = requests.Request(**request.request_parameters).prepare().url
            responses.add(responses.GET, url, body=self.mock_stream_response_page1)
            responses.add(responses.GET, self.test_s3_file_url, body=self.test_eicar, stream=True)

            result = self._run_cli(['stream', '--since', self.test_since, path])

            self._assert_text_result(
                result,
                expected_output=mock_polyswarm_api_results.text_local_artifacts(
                    self.test_hash_value,
                    os.path.join(path, self.test_hash_value))[0],
                expected_return_code=0,
            )

    @responses.activate
    def test_download_cat(self):
        with file_utils.temp_dir({self.test_hash_value: self.test_eicar}) as (path, files):
            request = self._create_download_request(self.test_hash_value)
            request.request_parameters.pop('stream')
            url = requests.Request(**request.request_parameters).prepare().url
            responses.add(responses.GET, url, body=self.test_eicar, stream=True)

            result = self._run_cli(['cat', self.test_hash_value])
            self._assert_text_result(
                result,
                expected_output=self.test_eicar.decode(),
                expected_return_code=0,
            )
