import logging
import os
from unittest import TestCase
import json
import yaml
import traceback

import vcr as vcr_
from deepdiff import DeepDiff
from click.testing import CliRunner
from pkg_resources import resource_filename

from polyswarm.client import polyswarm as client
from polyswarm_api.api import PolyswarmAPI

logger = logging.getLogger(__name__)

TestCase.maxDiff = None

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


vcr = vcr_.VCR(cassette_library_dir='tests/vcr',
               path_transformer=vcr_.VCR.ensure_suffix('.vcr'))


class BaseTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        self.click_vcr_folder = 'tests/vcr'
        self.click_vcr_suffix = 'click'
        self.test_runner = CliRunner()
        self.api_url = 'http://artifact-index-e2e:9696/v2'
        self.test_api_key = '11111111111111111111111111111111'
        self.api = PolyswarmAPI(self.test_api_key, community='gamma')
        self.test_hash_value = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
        self.test_eicar = b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
        self.test_s3_file_url = 'http://minio:9000/'\
                                'testing/testing/files/27/5a/02/'\
                                '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f?'\
                                'response-content-disposition=attachment%3B%20filename%3Dtesting%2F'\
                                'files%2F27%2F5a%2F02%'\
                                '2F275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f&'\
                                'response-content-type=application%2Foctet-stream&'\
                                'AWSAccessKeyId=AKIAIOSFODNN7EXAMPLE'\
                                '&Signature=VLCdYUh8skB6cRqo7RUfGrycsKo%3D&Expires=1573768889'

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
        commands = ['--api-key', self.test_api_key, '-u', self.api_url] + commands
        return self.test_runner.invoke(client.polyswarm_cli, commands, catch_exceptions=False)

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
    def _assert_json_equal(first, second):
        diff = DeepDiff(first, second, ignore_order=True)
        if diff:
            raise AssertionError('Input JSON\'s differ: %s' % diff)

    @staticmethod
    def _get_test_resource_file_path(filename):
        return resource_filename('tests.resources', filename)

    @staticmethod
    def _create_response(results, **kwargs):
        response = {'result': results, 'status': 'OK'}
        if kwargs:
            response['offset'] = kwargs.get('offset', None)
            response['limit'] = kwargs.get('limit', None)
            response['has_more'] = kwargs.get('has_more', True)
        return json.dumps(response)


