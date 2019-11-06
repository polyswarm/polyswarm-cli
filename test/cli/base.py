import os
from unittest import TestCase

from click.testing import CliRunner
import requests_mock
from pkg_resources import resource_string
import json
import traceback

from polyswarm_api.const import DEFAULT_GLOBAL_API, DEFAULT_COMMUNITY
from polyswarm_api.endpoint import PolyswarmRequestGenerator

from polyswarm import base


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class BaseTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_api_key = '963da5a463b0ab61fe0f96f82846490d'
        self.request_generator = PolyswarmRequestGenerator(DEFAULT_GLOBAL_API, DEFAULT_COMMUNITY)

        self.test_captured_output_file = '/tmp/output.txt'

    def setUp(self):
        self._remove_file(self.test_captured_output_file)

    @staticmethod
    def _remove_file(file_path):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except FileNotFoundError:
                print('File {file_path} does not exist'.format(**{'file_path': file_path}))
            except OSError:
                print('File {file_path} does not exist'.format(**{'file_path': file_path}))

    @staticmethod
    def _get_file_content(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    @staticmethod
    def _get_test_text_resource_content(resource):
        return resource_string('test.resources', resource).decode('utf-8')

    def _get_test_json_resource_content(self, resource):
        return json.loads(self._get_test_text_resource_content(resource))

    def _add_auth(self, req):
        if 'headers' not in req:
            req['headers'] = {}
        req['headers']['Authorization'] = self.test_api_key

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

    def _do_success_test(self, reqs,  output_format, output_path, commands, with_auth=True):

        result = self._do_test(reqs, output_format, commands, with_auth)
        self.assertEqual(result.exit_code, 0, msg=traceback.format_tb(result.exc_info[2]))
        if output_path:
            expected_output = self._get_test_text_resource_content(output_path)
            output = self._get_file_content(self.test_captured_output_file)
            self.assertEqual(output, expected_output)

    def _do_fail_test(self, reqs, output_format, output_path, commands, with_auth=True):
        result = self._do_test(reqs, output_format, commands, with_auth)

        self.assertNotEqual(result.exit_code, 0, msg=traceback.format_tb(result.exc_info[2]))
        if output_path:
            expected_output = self._get_test_text_resource_content(output_path)
            output = result.stdout
            self.assertEqual(output, expected_output)
