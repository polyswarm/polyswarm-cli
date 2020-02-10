import logging
import os
from unittest import TestCase
import re
import json
import difflib
import traceback
from deepdiff import DeepDiff
from click.testing import CliRunner
from pkg_resources import resource_string, resource_filename

from polyswarm_api.types import resources
from polyswarm import base
from polyswarm_api.api import PolyswarmAPI

logger = logging.getLogger(__name__)

TestCase.maxDiff = None

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class BaseTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.test_captured_output_file = '/tmp/output.txt'
        self.api_url = 'https://api.polyswarm.network/v2'
        self.test_api_key = '11111111111111111111111111111111'
        self.community = 'lima'
        self.request_generator = PolyswarmAPI(self.test_api_key, community=self.community).generator
        self.test_hash_value = '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f'
        self.test_query = '_exists_:lief.libraries'
        self.test_submission_uuid = '49091542211453596'
        self.test_hunt_id = '63433636835291189'
        self.test_since = '2880'
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

    def setUp(self):
        self._remove_file(self.test_captured_output_file)

    def _setup_mock_api_response(self, mock_server, request, response):
        request_parameters = self.convert_polyswarm_api_request_to_mock_request_parameters(request)
        mock_server.request(text=response, **request_parameters)

    @staticmethod
    def _setup_mock_url_response(mock_server, url, response):
        request_parameters = {'method': 'GET',
                              'url': url}
        mock_server.request(body=response, **request_parameters)

    def _setup_mock_api_download(self, mock_server, request, download_file):
        request_parameters = self.convert_polyswarm_api_request_to_mock_request_parameters(request)
        mock_server.request(body=download_file, **request_parameters)

    def _create_search_hash_request(self, hash_value, offset=None, limit=None):
        request = self.request_generator.search_hash(resources.Hash.from_hashable(hash_value))
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_search_metadata_request(self, query, offset=None, limit=None):
        request = self.request_generator.search_metadata(query)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_scan_submission_lookup_request(self, submission_uuid):
        request = self.request_generator.lookup_uuid(submission_uuid)
        return request

    def _create_scan_submission_submit_request(self, artifact):
        request = self.request_generator.submit(resources.LocalArtifact(artifact))
        return request

    def _create_scan_submission_rescan_request(self, hash_value, hash_type='sha256'):
        request = self.request_generator.rescan(resources.Hash(hash_value, hash_type))
        return request

    def _create_hunt_live_results_request(self, hunt_id, since, offset=None, limit=None):
        request = self.request_generator.live_hunt_results(hunt_id, since)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_hunt_historical_results_request(self, hunt_id, offset=None, limit=None):
        request = self.request_generator.historical_hunt_results(hunt_id)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_hunt_live_start_request(self, yara_file):
        request = self.request_generator.create_live_hunt(resources.YaraRuleset(dict(yara=open(yara_file).read())))
        return request

    def _create_hunt_historical_start_request(self, yara_file):
        request = self.request_generator.create_historical_hunt(resources.YaraRuleset(dict(yara=open(yara_file).read())))
        return request

    def _create_hunt_live_delete_request(self, hunt_id):
        request = self.request_generator.delete_live_hunt(hunt_id)
        return request

    def _create_hunt_historical_delete_request(self, hunt_id):
        request = self.request_generator.delete_historical_hunt(hunt_id)
        return request

    def _create_hunt_live_list_request(self, offset=None, limit=None):
        request = self.request_generator.live_list()
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_hunt_historical_list_request(self, offset=None, limit=None):
        request = self.request_generator.historical_list()
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_download_request(self, hash_value, path, hash_type='sha256'):
        request = self.request_generator.download(hash_value, hash_type, output_file=path)
        return request

    def _create_stream_request(self, since, offset=None, limit=None):
        request = self.request_generator.stream(since)
        self._add_pagination_params(request, offset, limit)
        return request

    @staticmethod
    def _add_pagination_params(request, offset, limit):
        if offset is not None and limit is not None:
            request.request_parameters['params']['offset'] = offset
            request.request_parameters['params']['limit'] = limit

    def convert_polyswarm_api_request_to_mock_request_parameters(self, request):
        request_parameters = request.request_parameters
        self._add_params_to_request_url(request_parameters)
        self._remove_keys(request_parameters, ['timeout', 'params', 'json', 'data', 'files', 'stream'])
        self._add_auth(request_parameters)
        return request_parameters

    def _add_params_to_request_url(self, request_parameters):
        if 'params' in request_parameters:
            request_parameters['url'] = '%s?%s' % (request_parameters['url'],
                                                   self._params_to_string(request_parameters['params']))

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
        return resource_string('tests.resources', resource).decode('utf-8')

    def _get_test_json_resource_content(self, resource):
        return json.loads(self._get_test_text_resource_content(resource))

    def _run_cli(self, commands):
        commands = [
                       '--api-key', self.test_api_key,
                       '-u', self.api_url,
                   ] + commands
        return self.test_runner.invoke(base.polyswarm, commands, catch_exceptions=False)

    def _assert_text_result(self, result, expected_output=None, expected_return_code=None):
        result_output = self._get_result_output(result)
        if expected_output is not None:
            self._assert_text_equal(result_output, expected_output)
        if expected_return_code is not None:
            self.assertEqual(expected_return_code, result.exit_code, msg=traceback.format_tb(result.exc_info[2]))

    def _assert_json_result(self, result, expected_output, expected_return_code):
        result_output = self._get_result_output(result)
        output = json.loads(result_output)
        # TODO: this fixes issues with unicode as when loading we always consider it is a unicode string
        #  to be removed once we drop support to python 2.7
        expected_output = json.loads(json.dumps(expected_output, sort_keys=True))
        if expected_output is not None:
            self._assert_json_equal(output, expected_output)
        if expected_return_code is not None:
            self.assertEqual(expected_return_code, result.exit_code, msg=traceback.format_tb(result.exc_info[2]))

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
        return resource_filename('tests.resources', filename)

    @staticmethod
    def _create_response(results, offset=None, limit=None, has_more=True):
        return json.dumps({'result': results, 'status': 'OK', 'offset': offset, 'limit': limit, 'has_more': has_more})


