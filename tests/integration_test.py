import os

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
        url = 'https://api.polyswarm.network/v2/search/hash/sha256?hash=275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
        responses.add(responses.GET, url, body=self.mock_search_response_page1)
        result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash_value])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0)

    @responses.activate
    def test_search_metadata(self):
        url = 'https://api.polyswarm.network/v2/search/metadata/query?query=_exists_%3Alief.libraries'
        responses.add(responses.GET, url, body=self.mock_metadata_search_response)
        result = self._run_cli(['--output-format', 'json', 'search', 'metadata', self.test_query])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.metadata(self)[0].json,
            expected_return_code=0)

    @responses.activate
    def test_scan_submission_lookup(self):
        url = 'https://api.polyswarm.network/v2/consumer/submission/lima/49091542211453596'
        responses.add(responses.GET, url, body=self.mock_submission_response)

        result = self._run_cli(['--output-format', 'json', '-c', self.community, 'lookup', self.test_submission_uuid])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_scan_submission_create(self):
        url = 'https://api.polyswarm.network/v2/consumer/submission/lima/49091542211453596'
        responses.add(responses.GET, url, body=self.mock_submission_response)
        url = 'https://api.polyswarm.network/v2/consumer/submission/lima'
        responses.add(responses.POST, url, body=self.mock_submission_response)

        malicious_file = self._get_test_resource_file_path('malicious')
        result = self._run_cli(['--output-format', 'json', '-c', self.community, 'scan', 'file', malicious_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_scan_submission_rescan(self):
        url = 'https://api.polyswarm.network/v2/consumer/submission/lima/rescan/sha256/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
        responses.add(responses.POST, url, body=self.mock_submission_response)
        url = 'https://api.polyswarm.network/v2/consumer/submission/lima/49091542211453596'
        responses.add(responses.GET, url, body=self.mock_submission_response)

        result = self._run_cli(['--output-format', 'json', '-c', self.community, 'rescan', self.test_hash_value])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.instances(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_results(self):
        url = 'https://api.polyswarm.network/v2/hunt/live/results?id=63433636835291189&since=2880'
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
        url = 'https://api.polyswarm.network/v2/hunt/historical/results?id=63433636835291189'
        responses.add(responses.GET, url, body=self.mock_hunt_historical_results_response_page1)

        result = self._run_cli(['--output-format', 'json', 'historical', 'results', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.historical_results(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_start(self):
        url = 'https://api.polyswarm.network/v2/hunt/live'
        responses.add(responses.POST, url, body=self.mock_hunt_response)

        yara_file = self._get_test_resource_file_path('eicar.yara')
        result = self._run_cli(['--output-format', 'json', 'live', 'create', yara_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_start_with_invalid_yara_file(self):
        url = 'https://api.polyswarm.network/v2/hunt/live'
        responses.add(responses.POST, url, body=self.mock_hunt_response)

        broken_yara_file = self._get_test_resource_file_path('broken.yara')
        result = self._run_cli(['--output-format', 'json', 'live', 'create', broken_yara_file])

        self._assert_text_result(
            result,
            expected_output='error [polyswarm.client.polyswarm]: Malformed yara file: line 1: syntax error, unexpected identifier',
            expected_return_code=2,
        )

    @responses.activate
    def test_historical_hunt_start(self):
        url = 'https://api.polyswarm.network/v2/hunt/historical'
        responses.add(responses.POST, url, body=self.mock_hunt_response)

        yara_file = self._get_test_resource_file_path('eicar.yara')
        result = self._run_cli(['--output-format', 'json', 'historical', 'start', yara_file])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_delete(self):
        url = 'https://api.polyswarm.network/v2/hunt/live?id=63433636835291189'
        responses.add(responses.DELETE, url, body=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'live', 'delete', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_historical_hunt_delete(self):
        url = 'https://api.polyswarm.network/v2/hunt/historical?id=63433636835291189'
        responses.add(responses.DELETE, url, body=self.mock_hunt_response)

        result = self._run_cli(['--output-format', 'json', 'historical', 'delete', self.test_hunt_id])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_live_hunt_list(self):
        url = 'https://api.polyswarm.network/v2/hunt/live/list'
        responses.add(responses.GET, url, body=self.mock_hunt_response_page1)

        result = self._run_cli(['--output-format', 'json', 'live', 'list'])

        self._assert_json_result(
            result,
            expected_output=mock_polyswarm_api_results.hunts(self)[0].json,
            expected_return_code=0,
        )

    @responses.activate
    def test_historical_hunt_list(self):
        url = 'https://api.polyswarm.network/v2/hunt/historical/list'
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
            url = 'https://api.polyswarm.network/v2/download/sha256/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
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
            url = 'https://api.polyswarm.network/v2/consumer/download/stream?since=2880'
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
            url = 'https://api.polyswarm.network/v2/download/sha256/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
            responses.add(responses.GET, url, body=self.test_eicar, stream=True)

            result = self._run_cli(['cat', self.test_hash_value])
            self._assert_text_result(
                result,
                expected_output=self.test_eicar.decode(),
                expected_return_code=0,
            )
