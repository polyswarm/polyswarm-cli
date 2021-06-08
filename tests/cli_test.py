from tests.utils.base_test_case import BaseTestCase, vcr
from tests.utils import file_utils


class IntegrationTest(BaseTestCase):
    """
        These tests mock the resource end-point, thus also sanity testing polyswarm-api.
    """
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


class HuntResultsTest(BaseTestCase):
    @vcr.use_cassette()
    def test_historical_hunt_results_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'historical', 'results', '16499733629565737'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_results_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'historical', 'results', '16499733629565737'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_results_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'live', 'results', '1876773693834725', '--since', '9999999'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_results_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'live', 'results', '1876773693834725', '--since', '9999999'])
        self._assert_text_result(result, self.click_vcr(result))


class LiveHuntTest(BaseTestCase):
    @vcr.use_cassette()
    def test_live_hunt_create_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'live', 'create', self._get_test_resource_file_path('eicar.yara')])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_create_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'live', 'create', self._get_test_resource_file_path('eicar.yara')])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_delete_json(self):
        result = self._run_cli(['--output-format', 'json', 'live', 'delete', '85659245822016383'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_delete_text(self):
        result = self._run_cli(['--output-format', 'text', 'live', 'delete', '84466777730273290'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_list_json(self):
        result = self._run_cli(['--output-format', 'json', 'live', 'list'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_list_text(self):
        result = self._run_cli(['--output-format', 'text', 'live', 'list'])
        self._assert_text_result(result, self.click_vcr(result))


class HistoricalHuntTest(BaseTestCase):
    @vcr.use_cassette()
    def test_historical_hunt_create_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'historical', 'start', self._get_test_resource_file_path('eicar.yara')])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_create_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'historical', 'start', self._get_test_resource_file_path('eicar.yara')])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_delete_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'historical', 'delete', '47234186287723204'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_delete_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'historical', 'delete', '94311373661871161'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_list_json(self):
        result = self._run_cli(['--output-format', 'json', 'historical', 'list'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_list_text(self):
        result = self._run_cli(['--output-format', 'text', 'historical', 'list'])
        self._assert_text_result(result, self.click_vcr(result))


class RulesetTest(BaseTestCase):
    @vcr.use_cassette()
    def test_ruleset_create_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rules', 'create', 'test', self._get_test_resource_file_path('eicar.yara')])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ruleset_get_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rules', 'view', '59706989547481262'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ruleset_update_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rules', 'update', '59706989547481262', '--name', 'test2'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ruleset_delete_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rules', 'delete', '59706989547481262'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ruleset_list_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rules', 'list'])
        self._assert_json_result(result, self.click_vcr(result))


class SubmissionTest(BaseTestCase):
    @vcr.use_cassette()
    def test_submission_lookup_json(self):
        result = self._run_cli([
            '--output-format', 'json', '-c', 'gamma', 'lookup', '82046699255546478'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_lookup_text(self):
        result = self._run_cli([
            '--output-format', 'text', '-c', 'gamma', 'lookup', '82046699255546478'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_create_json(self):
        result = self._run_cli([
            '--output-format', 'json', '-c', 'gamma', 'scan', 'file', self._get_test_resource_file_path('malicious')])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_create_text(self):
        result = self._run_cli([
            '--output-format', 'text', '-c', 'gamma', 'scan', 'file', self._get_test_resource_file_path('malicious')])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_rescan_json(self):
        result = self._run_cli([
            '--output-format', 'json', '-c', 'gamma', 'rescan', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_rescan_text(self):
        result = self._run_cli([
            '--output-format', 'text', '-c', 'gamma', 'rescan', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_rescan_id_json(self):
        result = self._run_cli([
            '--output-format', 'json', '-c', 'gamma', 'rescan-id', '82046699255546478'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_rescan_id_text(self):
        result = self._run_cli([
            '--output-format', 'text', '-c', 'gamma', 'rescan-id', '82046699255546478'])
        self._assert_text_result(result, self.click_vcr(result))


class SearchTest(BaseTestCase):
    @vcr.use_cassette()
    def test_search_hash_with_json_output(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'hash', self.test_hash_value])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_hash_with_text_output(self):
        result = self._run_cli([
            '--output-format', 'text', 'search', 'hash', self.test_hash_value])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_hash_with_no_results(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'hash', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0a'])
        self._assert_text_result(result, self.click_vcr(result), expected_return_code=1)

    @vcr.use_cassette()
    def test_search_metadata_with_json_output(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'metadata', 'hash.sha256:' + self.test_hash_value])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_metadata_with_text_output(self):
        result = self._run_cli([
            '--output-format', 'text', 'search', 'metadata', 'hash.sha256:' + self.test_hash_value])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_metadata_with_no_results(self):
        result = self._run_cli([
            '--output-format', 'text', 'search', 'metadata', 'hash.sha256:275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0a'])
        self._assert_text_result(result, self.click_vcr(result), expected_return_code=1)
