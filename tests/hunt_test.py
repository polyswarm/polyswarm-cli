from tests.utils.base_test_case import BaseTestCase, vcr


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
