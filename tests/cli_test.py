import shutil
import tempfile
import os
import json
import pytest
import yaml
from contextlib import contextmanager
from unittest import TestCase
import traceback

import vcr as vcr_
from click.testing import CliRunner
from pkg_resources import resource_filename

from polyswarm.client import polyswarm as client


vcr = vcr_.VCR(cassette_library_dir='tests/vcr',
               path_transformer=vcr_.VCR.ensure_suffix('.vcr'))


class BaseTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        self.cli = CliRunner()
        self.click_vcr_folder = 'tests/vcr'
        self.click_vcr_suffix = 'click'
        self.api_url = 'http://artifact-index-e2e:9696/v3'
        self.api_key = '11111111111111111111111111111111'
        self.community = 'gamma'
        self.eicar_hash = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'

    def _replace(self, replace, content):
        if replace:
            for source, replacement in replace:
                content = content.replace(source, replacement)
        return content

    def click_vcr(self, result, name='result', replace=None):
        test_name = self.id().rpartition('.')[2]
        file_name = '{}.{}'.format(test_name, self.click_vcr_suffix)
        file_path = os.path.join(os.getcwd(), self.click_vcr_folder, file_name)
        try:
            with open(file_path, 'r') as f:
                data = yaml.full_load(f)
            entry = data.get(name)
            if entry is None:
                entry = self._replace(replace, result.output)
                data[name] = entry
                with open(file_path, 'w') as f:
                    yaml.dump(data, f)
        except OSError:
            entry = self._replace(replace, result.output)
            data = {name: entry}
            with open(file_path, 'w') as f:
                yaml.dump(data, f)
        return entry

    def _run_cli(self, commands):
        commands = ['-a', self.api_key, '-u', self.api_url, '-c', self.community] + commands
        return self.cli.invoke(client.polyswarm_cli, commands, catch_exceptions=False)

    def _assert_text_result(self, result, expected_result, expected_return_code=0, replace=None):
        current_result = self._replace(replace, result.output)
        assert current_result == expected_result
        self.assertEqual(expected_return_code, result.exit_code, msg=traceback.format_tb(result.exc_info[2]))

    def _assert_json_result(self, results, expected_results, expected_return_code=0, replace=None):
        current_results = self._replace(replace, results.output)
        result_lines = current_results.splitlines()
        expected_lines = expected_results.splitlines()
        if len(result_lines) != len(expected_lines):
            raise AssertionError('Number of json lines does not match')
        self.assertEqual(expected_return_code, results.exit_code, msg=traceback.format_tb(results.exc_info[2]))
        for result, expected_result in zip(result_lines, expected_lines):
            result = json.loads(result)
            expected_result = json.loads(expected_result)
            assert result == expected_result

    @staticmethod
    def resource(filename):
        return resource_filename('tests', filename)


class DownloadTest(BaseTestCase):
    @vcr.use_cassette()
    def test_download(self):
        with tempfile.TemporaryDirectory() as path:
            result = self._run_cli([
                '-u', self.api_url, 'download', '-d', path, self.eicar_hash])
            expected_result = self.click_vcr(result, replace=((path, 'temporary_folder'),))
            self._assert_text_result(result, expected_result, replace=((path, 'temporary_folder'),))

    @vcr.use_cassette()
    def test_download_stream(self):
        with tempfile.TemporaryDirectory() as path:
            result = self._run_cli(['--parallel', '1', '-u', self.api_url, 'stream', '--since', '2880', path])
            expected_result = self.click_vcr(result, replace=((path, 'temporary_folder'),))
            self._assert_text_result(result, expected_result, replace=((path, 'temporary_folder'),))

    @vcr.use_cassette()
    def test_download_cat(self):
        with tempfile.TemporaryDirectory() as path:
            result = self._run_cli(['-u', self.api_url, 'cat', self.eicar_hash])
            expected_result = self.click_vcr(result, replace=((path, 'temporary_folder'),))
            self._assert_text_result(result, expected_result, replace=((path, 'temporary_folder'),))


class HuntResultsTest(BaseTestCase):
    @vcr.use_cassette()
    def test_historical_hunt_results_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'historical', 'results', '76083665328102613'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_results_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'historical', 'results', '76083665328102613'])
        self._assert_text_result(result, self.click_vcr(result))


    @vcr.use_cassette()
    def test_historical_hunt_results_private_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'historical', 'results', '76083665328102613', '--private'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_feed_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'live', 'feed', '--since', '9999999'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_feed_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'live', 'feed', '--since', '9999999'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_feed_private_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'live', 'feed', '--since', '9999999', '--private'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_result_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'live', 'result', '11704609705052856'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_result_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'live', 'result', '11704609705052856'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_result_delete_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'live', 'results-delete', '11704609705052856'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_result_delete_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'live', 'results-delete', '11704609705052856'])
        self._assert_text_result(result, self.click_vcr(result))


class LiveHuntTest(BaseTestCase):
    @vcr.use_cassette()
    def test_live_hunt_start_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'live', 'start', '17388152480558505'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_start_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'live', 'start', '17388152480558505'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_stop_json(self):
        result = self._run_cli(['--output-format', 'json', 'live', 'stop', '17388152480558505'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_live_hunt_stop_text(self):
        result = self._run_cli(['--output-format', 'text', 'live', 'stop', '17388152480558505'])
        self._assert_text_result(result, self.click_vcr(result))


class HistoricalHuntTest(BaseTestCase):
    @vcr.use_cassette()
    def test_historical_hunt_create_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'historical', 'start', self.resource('eicar.yara')])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_create_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'historical', 'start', self.resource('eicar.yara')])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_delete_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'historical', 'delete', '75914219779430298'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_historical_hunt_delete_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'historical', 'delete', '96916002705221564'])
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
            '--output-format', 'json', 'rules', 'create', 'test', self.resource('eicar.yara')])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ruleset_view_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rules', 'view', '27214252780064715'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ruleset_update_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rules', 'update', '71213140536342873', '--name', 'test2'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ruleset_delete_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rules', 'delete', '71213140536342873'])
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
            '--output-format', 'json', 'lookup', '79185011799085464'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_lookup_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'lookup', '79185011799085464'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_create_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'scan', 'file', self.resource('malicious')])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_create_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'scan', 'file', self.resource('malicious')])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_rescan_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rescan', self.eicar_hash])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_rescan_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'rescan', self.eicar_hash])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_rescan_id_json(self):
        result = self._run_cli([
            '--output-format', 'json', 'rescan-id', '79185011799085464'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_submission_rescan_id_text(self):
        result = self._run_cli([
            '--output-format', 'text', 'rescan-id', '79185011799085464'])
        self._assert_text_result(result, self.click_vcr(result))


class SearchTest(BaseTestCase):
    @vcr.use_cassette()
    def test_search_hash_with_json_output(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'hash', self.eicar_hash])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_hash_with_text_output(self):
        result = self._run_cli([
            '--output-format', 'text', 'search', 'hash', self.eicar_hash])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_hash_with_no_results(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'hash', '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0a'])
        self._assert_text_result(result, self.click_vcr(result), expected_return_code=1)

    @vcr.use_cassette()
    def test_search_metadata_with_json_output(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'metadata', 'hash.sha256:' + self.eicar_hash])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_metadata_with_text_output(self):
        result = self._run_cli([
            '--output-format', 'text', 'search', 'metadata', 'hash.sha256:' + self.eicar_hash])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_search_metadata_with_no_results(self):
        result = self._run_cli([
            '--output-format', 'text', 'search', 'metadata', 'hash.sha256:275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0a'])
        self._assert_text_result(result, self.click_vcr(result), expected_return_code=1)

class IOCTest(BaseTestCase):

    @vcr.use_cassette()
    def test_ioc_by_hash(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'ioc', 'sha256', '18e5b8fe65e8f73c3a4a637c258c02aeec8a6ab702b15b7ee73f5631a9879e40'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ioc_by_hash_no_results(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'ioc', 'sha256', self.eicar_hash])
        self._assert_text_result(result, self.click_vcr(result), expected_return_code=1)

    @vcr.use_cassette()
    def test_ioc_artifact_by_ioc(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'ioc', 'ip', '2.2.2.2'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_ioc_artifact_by_ioc_no_results(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'ioc', 'ip', '192.0.0.1'])
        self._assert_text_result(result, self.click_vcr(result), expected_return_code=1)


    @vcr.use_cassette()
    def test_check_known_hosts(self):
        result = self._run_cli([
            '--output-format', 'json', 'search', 'known', '-d', 'www.polyswarm.io', '-p', '1.1.1.1'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_add_known_host(self):
        result = self._run_cli([
            '--output-format', 'json', 'known', 'add', 'domain', 'www.polyswarm.plus', 'some list'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_update_known_host(self):
        result = self._run_cli([
            '--output-format', 'json', 'known', 'update', '1', 'domain', 'www.google.com', 'some list'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_delete_known_host(self):
        result = self._run_cli([
            '--output-format', 'json', 'known', 'delete', '5'])
        self._assert_json_result(result, self.click_vcr(result))


class SandoxTest(BaseTestCase):
    @vcr.use_cassette()
    def test_sandbox_file(self):
        result = self._run_cli([
            '--output-format', 'json', 'sandbox', 'instance', 'triage', '59710030898207379'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_sandbox_instance_internet_disabled(self):
        result = self._run_cli([
            '--output-format', 'json', 'sandbox', 'instance', 'triage', '73332334527130690', '--internet-disabled'])
        self._assert_json_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_sandbox_file_not_found(self):
        result = self._run_cli([
            '--output-format', 'json', 'sandbox', 'instance', 'triage', '86147028965243380'])
        self._assert_text_result(result, self.click_vcr(result), expected_return_code=1)

    @vcr.use_cassette()
    def test_sandbox_list(self):
        result = self._run_cli([
            '--output-format', 'json', 'sandbox', 'providers'])
        self._assert_text_result(result, self.click_vcr(result))


class SandboxTaskTest(BaseTestCase):
    @vcr.use_cassette()
    def test_sandboxtask_status(self):
        result = self._run_cli([
            '--output-format', 'json', 'sandbox', 'lookup-id', '83909716318937863'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_sandboxtask_list(self):
        result = self._run_cli([
            '--output-format', 'json', 'sandbox', 'search', 'a709f37b3a50608f2e9830f92ea25da04bfa4f34d2efecfd061de9f29af02427'])
        self._assert_text_result(result, self.click_vcr(result))

    @vcr.use_cassette()
    def test_sandboxtask_latest(self):
        result = self._run_cli([
            '--output-format', 'json', 'sandbox', 'lookup', 'triage', 'a709f37b3a50608f2e9830f92ea25da04bfa4f34d2efecfd061de9f29af02427'])
        self._assert_text_result(result, self.click_vcr(result))