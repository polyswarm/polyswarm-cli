import os

import responses

from tests.utils.base_test_case import BaseTestCase, vcr
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

    @vcr.use_cassette()
    def test_search_hash(self):
        result = self._run_cli(['--output-format', 'json', 'search', 'hash', self.test_hash_value])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_metadata(self):
        result = self._run_cli(['--output-format', 'json', 'search', 'metadata', '_exists_:artifact.sha256'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_scan_submission_lookup(self):
        result = self._run_cli(['--output-format', 'json', '-c', 'gamma', 'lookup', '19610779111217241'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_scan_submission_create(self):
        malicious_file = self._get_test_resource_file_path('malicious')
        result = self._run_cli([
            '--output-format', 'json',
            '-c', 'gamma',
            'scan', 'file', malicious_file,
        ])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_scan_submission_rescan(self):
        result = self._run_cli(['--output-format', 'json', '-c', 'gamma', 'rescan', self.test_hash_value])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_results(self):
        result = self._run_cli([
            '--output-format', 'json', 'live', 'results', '26105308820047659', '--since', '2880'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_results(self):
        result = self._run_cli(['--output-format', 'json', 'historical', 'results', '39972292131000736'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_start(self):
        yara_file = self._get_test_resource_file_path('eicar.yara')
        result = self._run_cli(['--output-format', 'json', 'live', 'create', yara_file])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_start_with_invalid_yara_file(self):
        broken_yara_file = self._get_test_resource_file_path('broken.yara')
        result = self._run_cli(['--output-format', 'json', 'live', 'create', broken_yara_file])
        self._assert_text_result(
            result,
            'error [polyswarm.client.polyswarm]: Malformed yara file: line 1: syntax error, unexpected identifier\n',
            expected_return_code=2,
        )

    @vcr.use_cassette()
    def test_historical_hunt_start(self):
        yara_file = self._get_test_resource_file_path('eicar.yara')
        result = self._run_cli(['--output-format', 'json', 'historical', 'start', yara_file])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_delete(self):
        result = self._run_cli(['--output-format', 'json', 'live', 'delete', '1876773693834725'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_delete(self):
        result = self._run_cli(['--output-format', 'json', 'historical', 'delete', '93536118162554562'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_list(self):
        result = self._run_cli(['--output-format', 'json', 'live', 'list'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_list(self):
        result = self._run_cli(['--output-format', 'json', 'historical', 'list'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_download(self):
        with file_utils.temp_dir({self.test_hash_value: self.test_eicar}) as (path, files):
            result = self._run_cli([
                '-u', self.api_url + '/consumer', 'download', '-d', path, self.test_hash_value])
            expected_result = self.click_vcr(result, replace=((path, 'temporary_folder'),))
            self._assert_text_result(result, expected_result, replace=((path, 'temporary_folder'),))

    @vcr.use_cassette()
    def test_download_stream(self):
        with file_utils.temp_dir({self.test_hash_value: self.test_eicar}) as (path, files):
            result = self._run_cli(['stream', '--since', '2880', path])
            expected_result = self.click_vcr(result, replace=((path, 'temporary_folder'),))
            self._assert_text_result(result, expected_result, replace=((path, 'temporary_folder'),))

    @vcr.use_cassette()
    def test_download_cat(self):
        with file_utils.temp_dir({self.test_hash_value: self.test_eicar}) as (path, files):
            result = self._run_cli(['-u', self.api_url + '/consumer', 'cat', self.test_hash_value])
            expected_result = self.click_vcr(result, replace=((path, 'temporary_folder'),))
            self._assert_text_result(result, expected_result, replace=((path, 'temporary_folder'),))
