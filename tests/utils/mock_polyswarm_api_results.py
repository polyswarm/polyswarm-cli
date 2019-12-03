import os

from polyswarm_api.types import resources
from polyswarm_api.api import PolyswarmAPI


def instances(test):
    values = []
    values.append(resources.ArtifactInstance(
        {'account_id': '1', 'artifact_id': '11611818710765483', 'assertions': [
            {'author': '0x05328f171b8c1463eaFDACCA478D9EE6a1d923F8', 'author_name': 'eicar',
             'bid': '1000000000000000000', 'engine': {'description': 'eicar', 'name': 'eicar', 'tags': []},
             'mask': True, 'metadata': {'malware_family': 'Eicar Test File', 'scanner': {
                'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}, 'verdict': True}],
         'community': 'gamma', 'country': '', 'created': '2019-11-07T19:18:00.265903',
         'extended_type': 'EICAR virus test files', 'failed': False,
         'filename': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f',
         'first_seen': '2019-11-01T21:33:53.292099', 'id': 49091542211453596, 'last_seen': '2019-11-07T16:18:00.269290',
         'md5': '44d88612fea8a8f36de82e1278abb02f', 'metadata': None, 'mimetype': 'text/plain', 'result': True,
         's3_file_name': 'testing/files/27/5a/02/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f',
         'sha1': '3395856ce81f2b7382dee72602f798b642f14140',
         'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'size': 68, 'type': 'FILE',
         'votes': [{'arbiter': '0xF870491ea0F53F67846Eecb57855284D8270284D', 'vote': True}], 'window_closed': True},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def text_instances():
    values = []
    values.append(
        """============================= Artifact Instance =============================
[94mSubmission id: 49091542211453596[0m
[92mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01 21:33:53.292099
Last seen: 2019-11-07 16:18:00.269290
Filename: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
Community: gamma
Country: 
Scan permalink: https://polyswarm.network/scan/results/49091542211453596
[91mDetections: 1/1 engines reported malicious[0m
[91meicar: Malicious, metadata: {"malware_family": "Eicar Test File", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}}}[0m

""")
    return values


def live_results(test):
    values = []
    values.append(resources.HuntResult(
        {'artifact': {'extended_type': 'EICAR virus test files', 'first_seen': '2019-11-01T21:33:53.292099',
                      'id': '11611818710765483', 'last_seen': '2019-11-12T15:52:00.702928',
                      'md5': '44d88612fea8a8f36de82e1278abb02f', 'metadata': None, 'mimetype': 'text/plain',
                      's3_file_name': None, 'sha1': '3395856ce81f2b7382dee72602f798b642f14140',
                      'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'size': 68},
         'created': '2019-11-07T19:06:22.630556', 'historicalscan_id': None, 'id': '86273842846244087',
         'livescan_id': '63433636835291189', 'rule_name': 'eicar_substring_test',
         'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'tags': ''},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def text_live_results():
    values = []
    values.append(
        """Match on rule eicar_substring_test
[92mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01 21:33:53.292099
Last seen: 2019-11-12 15:52:00.702928

""")
    return values


def historical_results(test):
    values = []
    values.append(resources.HuntResult(
        {'artifact': {'extended_type': 'EICAR virus test files', 'first_seen': '2019-11-01T21:33:53.292099',
                      'id': '11611818710765483', 'last_seen': '2019-11-12T15:52:00.702928',
                      'md5': '44d88612fea8a8f36de82e1278abb02f', 'metadata': None, 'mimetype': 'text/plain',
                      's3_file_name': None, 'sha1': '3395856ce81f2b7382dee72602f798b642f14140',
                      'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'size': 68},
         'created': '2019-11-04T18:40:02.063064', 'historicalscan_id': '47190397989086018', 'id': '36730172447808985',
         'livescan_id': None, 'rule_name': 'eicar_substring_test',
         'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'tags': ''},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def text_hisotrical_results():
    values = []
    values.append(
        """Match on rule eicar_substring_test
[92mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01 21:33:53.292099
Last seen: 2019-11-12 15:52:00.702928

""")
    return values


def hunts(test):
    values = []
    values.append(resources.Hunt(
        {'active': True, 'created': '2019-11-13T16:27:45.013226', 'id': '61210404295535902', 'status': 'SUCCESS'},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def text_hunts():
    values = []
    values.append(
        """[94mHunt Id: 61210404295535902[0m
Active: True
Created at: 2019-11-13 16:27:45.013226

""")
    return values


def text_detele_hunts():
    values = []
    values.append(
        """[93mSuccessfully deleted Hunt:[0m
[94mHunt Id: 61210404295535902[0m
Active: True
Created at: 2019-11-13 16:27:45.013226

""")
    return values


def artifact_archives(test):
    values = []
    values.append(resources.ArtifactArchive(
        {'id': '1', 'community': 'gamma', 'created': '2019-11-14T16:30:00.888191', 's3_path': 's3/malicious'},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def local_artifacts(hash_value, path):
    values = []
    full_path = os.path.join(path, hash_value)
    values.append(resources.LocalArtifact(path=full_path, artifact_name=hash_value, analyze=False))
    return values


def text_local_artifacts(filename, full_path):
    values = []
    values.append(
        """Successfully downloaded artifact {} to {}

""".format(os.path.basename(filename), full_path))
    return values


def cat_request(data):
    class Request:
        def __init__(self, status_code=200, json=None, content=None):
            self.status_code = status_code
            self.json = json
            self.content = content

        def iter_content(self, chunk_size=None):
            yield self.content

    return Request(content=data)


def scores(test):
    values = []
    values.append(resources.PolyScore(
        {'scores': {'56977143704899183': 0.00024050482800527995, '11611818710765483': 0.00024050482800527995,
                    '49091542211453596': 0.00024050482800527995, }},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def stream_results(s3_file_url):
    values = []
    values.append(
        {'community': 'gamma', 'created': '2019-11-28T18:04:38.923000',
         'id': '67497956521144077',
         's3_path': s3_file_url})
    return values
