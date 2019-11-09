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

    @staticmethod
    def _setup_mock_response(mock_server, request, response):
        mock_server.request(text=response, **request)

    def _create_hash_request(self, file_hash):
        request = self.request_generator.search_hash(polyswarm_api_to_hash(file_hash))
        self.convert_polyswarm_api_request_to_mock_request(request)
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

    def _create_metadata_request(self, query, with_instances=True, with_metadata=True):
        request = self.request_generator.search_metadata(MetadataQuery(query), with_instances, with_metadata)
        self.convert_polyswarm_api_request_to_mock_request(request)
        return request

    @staticmethod
    def _remove_keys(request, params):
        for parameter in params:
            if parameter in request:
                del request[parameter]

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

    def _setup_mock_server_response(self, request, response, with_auth=True):
        self._remove_keys(request)
        with requests_mock.Mocker() as mock:
            if with_auth:
                self._add_auth(request)
            mock.request(text=response, **request)

    def _run_cli(self, commands):
        commands = ['--api-key', self.test_api_key,
                    '--output-file', self.test_captured_output_file] + commands
        return self.test_runner.invoke(base.polyswarm, commands)

    def _assert_text_result(self, result, expected_output, expected_return_code):
        output = self._get_result_output(result)
        self._assert_text_equal(output, expected_output)
        self.assertEqual(result.exit_code, expected_return_code, msg=traceback.format_tb(result.exc_info[2]))

    def _assert_json_result(self, result, expected_output, expected_return_code):
        result_output = self._get_result_output(result)
        try:
            output = json.loads(result_output)
        except json.JSONDecodeError as e:
            print('Error JSON decoding [%s]' % result_output)
            raise e
        self._assert_json_equal(output, expected_output)
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

    @staticmethod
    def mock_logger(msg, *args, **kwargs):
        """
        Click's CliRunner doesn't capture logging messages, thus we need to patch it in tests so it will use
        the standard output.
        """
        print(msg % args)

    def _do_test(self, reqs, output_format, commands, with_auth=True):
        bad_keys = ['params', 'json']

        cmd = ['--api-key', self.test_api_key, '--output-format', output_format,
               '--output-file', self.test_captured_output_file]
        cmd.extend(commands)

        if reqs:
            with requests_mock.Mocker() as mock:
                for req, result in reqs:
                    if with_auth:
                        self._add_auth(req)
                    for p in bad_keys:
                        if p in req:
                            del req[p]
                    mock.request(text=result, **req)
                return self.test_runner.invoke(base.polyswarm, cmd)

        return self.test_runner.invoke(base.polyswarm, cmd)

    def _do_success_test(self, reqs, output_format, output_path, commands, with_auth=True):

        result = self._do_test(reqs, output_format, commands, with_auth)
        self.assertEqual(result.exit_code, 0, msg=traceback.format_tb(result.exc_info[2]))
        if output_path:
            expected_output = self._get_test_text_resource_content(output_path)
            output = self._get_text_file_content(self.test_captured_output_file)
            self.assertEqual(output, expected_output)

    def _do_fail_test(self, reqs, output_format, output_path, commands, with_auth=True):
        result = self._do_test(reqs, output_format, commands, with_auth)

        self.assertNotEqual(result.exit_code, 0, msg=traceback.format_tb(result.exc_info[2]))
        if output_path:
            expected_output = self._get_test_text_resource_content(output_path)
            output = result.stdout
            self.assertEqual(output, expected_output)
