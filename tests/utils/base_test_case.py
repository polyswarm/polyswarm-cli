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

from polyswarm_api import resources
from polyswarm.client import polyswarm as client
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
        self.api = PolyswarmAPI(self.test_api_key, community=self.community)
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

    def _create_search_hash_request(self, hash_value, offset=None, limit=None):
        h = resources.Hash.from_hashable(hash_value)
        request = resources.ArtifactInstance.search_hash(self.api, h.hash, h.hash_type)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_search_metadata_request(self, query, offset=None, limit=None):
        request = resources.Metadata.get(self.api, query=query)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_scan_submission_lookup_request(self, submission_uuid):
        request = resources.ArtifactInstance.lookup_uuid(self.api, submission_uuid)
        return request

    def _create_scan_submission_submit_request(self, artifact):
        a = resources.LocalArtifact.from_path(self.api, artifact)
        request = resources.ArtifactInstance.submit(self.api, a, a.artifact_name, a.artifact_type.name)
        return request

    def _create_scan_submission_rescan_request(self, hash_value, hash_type='sha256'):
        h = resources.Hash(hash_value, hash_type)
        request = resources.ArtifactInstance.rescan(self.api, h.hash, h.hash_type)
        return request

    def _create_hunt_live_results_request(self, hunt_id, since, offset=None, limit=None):
        request = resources.HuntResult.live_hunt_results(self.api, hunt_id, since)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_hunt_historical_results_request(self, hunt_id, offset=None, limit=None):
        request = resources.HuntResult.historical_hunt_results(self.api, hunt_id)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_hunt_live_start_request(self, yara_file):
        request = resources.LiveHunt.create(self.api, yara=open(yara_file).read())
        return request

    def _create_hunt_historical_start_request(self, yara_file):
        request = resources.HistoricalHunt.create(self.api, yara=open(yara_file).read())
        return request

    def _create_hunt_live_delete_request(self, hunt_id):
        request = resources.LiveHunt.delete(self.api, id=hunt_id)
        return request

    def _create_hunt_historical_delete_request(self, hunt_id):
        request = resources.HistoricalHunt.delete(self.api, id=hunt_id)
        return request

    def _create_hunt_live_list_request(self, offset=None, limit=None):
        request = resources.LiveHunt.list(self.api)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_hunt_historical_list_request(self, offset=None, limit=None):
        request = resources.HistoricalHunt.list(self.api)
        self._add_pagination_params(request, offset, limit)
        return request

    def _create_download_request(self, hash_value, hash_type='sha256'):
        request = resources.LocalHandle.download(self.api, hash_value, hash_type)
        return request

    def _create_stream_request(self, since, offset=None, limit=None):
        request = resources.ArtifactArchive.stream(self.api, since)
        self._add_pagination_params(request, offset, limit)
        return request

    @staticmethod
    def _add_pagination_params(request, offset, limit):
        if offset is not None and limit is not None:
            request.request_parameters['params']['offset'] = offset
            request.request_parameters['params']['limit'] = limit

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

    def _run_cli(self, commands):
        commands = [
                       '--api-key', self.test_api_key,
                       '-u', self.api_url,
                   ] + commands
        return self.test_runner.invoke(client.polyswarm, commands, catch_exceptions=False)

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


