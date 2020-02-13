import os
from unittest import TestCase
import requests_mock
import re
import json
import difflib
import traceback
from deepdiff import DeepDiff

from click.testing import CliRunner
from pkg_resources import resource_string, resource_filename

from polyswarm_api import const as polyswarm_api_const
from polyswarm_api.endpoint import PolyswarmRequestGenerator
from polyswarm_api.types.hash import to_hash as polyswarm_api_to_hash
from polyswarm_api.types.query import MetadataQuery
from polyswarm_api.log import logger

from polyswarm import base

TestCase.maxDiff = None

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class BaseTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '963da5a463b0ab61fe0f96f82846490d'
        self.request_generator = PolyswarmRequestGenerator(polyswarm_api_const.DEFAULT_GLOBAL_API,
                                                           polyswarm_api_const.DEFAULT_COMMUNITY)

        self.test_captured_output_file = '/tmp/output.txt'

    def setUp(self):
        self._remove_file(self.test_captured_output_file)

    def _setup_mock_response(self, mock_server, request, response, with_auth=True):
        self._remove_keys(request, ['params', 'json'])
        if with_auth:
            self._add_auth(request)
        mock_server.request(text=response, **request)

    def _create_search_hash_request(self, file_hash, with_instances=True, with_metadata=True):
        request = self.request_generator.search_hash(polyswarm_api_to_hash(file_hash), with_instances, with_metadata)
        self.convert_polyswarm_api_request_to_mock_request(request)
        return request

    def _create_search_metadata_request(self, query, with_instances=True, with_metadata=True):
        request = self.request_generator.search_metadata(MetadataQuery(query), with_instances, with_metadata)
        self.convert_polyswarm_api_request_to_mock_request(request)
        return request

    def _create_hunt_live_list_request(self):
        request = self.request_generator.live_list()
        self.convert_polyswarm_api_request_to_mock_request(request)
        print(request)
        return request

    def convert_polyswarm_api_request_to_mock_request(self, request):
        self._add_params_to_request_url(request)
        self._remove_keys(request, ['params', 'json'])
        self._add_auth(request)

    def _add_params_to_request_url(self, request):
        if 'params' in request:
            request['url'] = '%s?%s' % (request['url'], self._params_to_string(request['params']))

    @staticmethod
    def _params_to_string(params):
        return '&'.join(['%s=%s' % (param, value) for param, value in params.items()])

    @staticmethod
    def _remove_keys(request, params):
        for param in params:
            if param in request:
                del request[param]

    def _add_auth(self, request):
        if 'headers' not in request:
            request['headers'] = {}
        request['headers']['Authorization'] = self.test_api_key

    @staticmethod
    def _remove_file(file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except (FileNotFoundError, OSError) as e:
                logger.warning('File %s does not exist', file_path)
                logger.exception(e)

    @staticmethod
    def _get_text_file_content(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    @staticmethod
    def _get_json_file_content(file_path):
        with open(file_path, 'r') as file:
            return json.loads(file.read())

    @staticmethod
    def _get_test_text_resource_content(resource):
        return resource_string('test.resources', resource).decode('utf-8')

    def _get_test_json_resource_content(self, resource):
        return json.loads(self._get_test_text_resource_content(resource))

    def _run_cli(self, commands):
        commands = ['--api-key', self.test_api_key,
                    '--output-file', self.test_captured_output_file] + commands
        return self.test_runner.invoke(base.polyswarm, commands)

    def _assert_text_result(self, result, expected_output=None, expected_return_code=None):
        result_output = self._get_result_output(result)
        if expected_output is not None:
            self._assert_text_equal(result_output, expected_output)
        if expected_return_code is not None:
            self.assertEqual(result.exit_code, expected_return_code, msg=traceback.format_tb(result.exc_info[2]))

    def _assert_json_result(self, result, expected_output, expected_return_code):
        result_output = self._get_result_output(result)
        output = json.loads(result_output)
        if expected_output is not None:
            self._assert_json_equal(output, expected_output)
        if expected_return_code is not None:
            self.assertEqual(result.exit_code, expected_return_code, msg=traceback.format_tb(result.exc_info[2]))

    def _get_result_output(self, result):
        output = ''
        if result.output:
            output = result.output
        if os.path.isfile(self.test_captured_output_file):
            output += self._get_text_file_content(self.test_captured_output_file)
        return output

    @staticmethod
    def _assert_json_equal(first, second):
        diff = DeepDiff(first, second, ignore_order=True)
        if diff:
            raise AssertionError('Input JSON\'s differ: %s' % diff)

    def _assert_text_equal(self, first, second):
        diff = list(difflib.ndiff(self._text_to_normalized_lines(first),
                                  self._text_to_normalized_lines(second),
                                  linejunk=difflib.IS_LINE_JUNK))
        if self._is_different(diff):
            raise AssertionError('Input texts differ: %s' % '\n'.join(diff))

    @staticmethod
    def _text_to_normalized_lines(text):
        return [re.sub(r'[^\S\r\n]+', ' ', diff_line)
                for diff_line in text.splitlines() if not re.match(r'^[\s\n]*$', diff_line)]

    def _is_different(self, diff):
        result = False
        for line in diff:
            if self._is_diff_line_different(line):
                result = True
                break
        return result

    @staticmethod
    def _is_diff_line_different(diff_line):
        return diff_line.startswith('+') or diff_line.startswith('-') or diff_line.startswith('?')

    @staticmethod
    def _get_test_resource_file_path(filename):
        return resource_filename('test.resources', filename)

