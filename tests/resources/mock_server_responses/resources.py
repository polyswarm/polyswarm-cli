import os

from polyswarm_api.types import resources
from polyswarm_api.api import PolyswarmAPI


def instances(test):
    values = []
    values.append(resources.ArtifactInstance(
        {u'account_id': u'1', u'artifact_id': u'11611818710765483', u'assertions': [{u'author': u'0x05328f171b8c1463eaFDACCA478D9EE6a1d923F8', u'author_name': u'eicar', u'bid': u'1000000000000000000', u'engine': {u'description': u'eicar', u'name': u'eicar', u'tags': []}, u'mask': True, u'metadata': {u'malware_family': u'Eicar Test File', u'scanner': {u'environment': {u'architecture': u'x86_64', u'operating_system': u'Linux'}}}, u'verdict': True}], u'community': u'gamma', u'country': u'', u'created': u'2019-11-07T19:18:00.265903', u'extended_type': u'EICAR virus test files', u'failed': False, u'filename': u'275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'first_seen': u'2019-11-01T21:33:53.292099', u'id': 49091542211453596, u'last_seen': u'2019-11-07T16:18:00.269290', u'md5': u'44d88612fea8a8f36de82e1278abb02f', u'metadata': None, u'mimetype': u'text/plain', u'result': True, u's3_file_name': u'testing/files/27/5a/02/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'sha1': u'3395856ce81f2b7382dee72602f798b642f14140', u'sha256': u'275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'size': 68, u'submission_id': 44664431668105478, u'submission_uuid': u'56944690-6376-44d3-8bff-00c217ccb272', u'type': u'FILE', u'votes': [{u'arbiter': u'0xF870491ea0F53F67846Eecb57855284D8270284D', u'vote': True}], u'window_closed': True},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community=u'gamma'),
    ))
    return values


def text_instances():
    values = []
    values.append(
        u"""[92mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01T21:33:53.292099
Filename: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
PolyScore: 0.00024050482800527995
Scan permalink: https://polyswarm.network/scan/results/56944690-6376-44d3-8bff-00c217ccb272
[91mDetections: 1/1 engines reported malicious[0m
[91meicar: Malicious, metadata: {'malware_family': 'Eicar Test File', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}[0m

""")
    return values


def live_results(test):
    values = []
    values.append(resources.HuntResult(
        {u'artifact': {u'extended_type': u'EICAR virus test files', u'first_seen': u'2019-11-01T21:33:53.292099', u'id': u'11611818710765483', u'last_seen': u'2019-11-12T15:52:00.702928', u'md5': u'44d88612fea8a8f36de82e1278abb02f', u'metadata': None, u'mimetype': u'text/plain', u's3_file_name': None, u'sha1': u'3395856ce81f2b7382dee72602f798b642f14140', u'sha256': u'275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'size': 68}, u'created': u'2019-11-07T19:06:22.630556', u'historicalscan_id': None, u'id': u'86273842846244087', u'livescan_id': u'63433636835291189', u'rule_name': u'eicar_substring_test', u'sha256': u'275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'tags': u''},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community=u'gamma'),
    ))
    return values


def text_live_results():
    values = []
    values.append(
        u"""Match on rule eicar_substring_test
[92mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01 21:33:53.292099

""")
    return values


def hisotrical_results(test):
    values = []
    values.append(resources.HuntResult(
        {u'artifact': {u'extended_type': u'EICAR virus test files', u'first_seen': u'2019-11-01T21:33:53.292099', u'id': u'11611818710765483', u'last_seen': u'2019-11-12T15:52:00.702928', u'md5': u'44d88612fea8a8f36de82e1278abb02f', u'metadata': None, u'mimetype': u'text/plain', u's3_file_name': None, u'sha1': u'3395856ce81f2b7382dee72602f798b642f14140', u'sha256': u'275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'size': 68}, u'created': u'2019-11-04T18:40:02.063064', u'historicalscan_id': u'47190397989086018', u'id': u'36730172447808985', u'livescan_id': None, u'rule_name': u'eicar_substring_test', u'sha256': u'275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'tags': u''},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community=u'gamma'),
    ))
    return values


def text_hisotrical_results():
    values = []
    values.append(
        u"""Match on rule eicar_substring_test
[92mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01 21:33:53.292099

""")
    return values


def hunts(test):
    values = []
    values.append(resources.Hunt(
        {u'active': True, u'created': u'2019-11-13T16:27:45.013226', u'id': u'61210404295535902', u'status': u'SUCCESS'},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community=u'gamma'),
    ))
    return values


def text_hunts():
    values = []
    values.append(
        u"""[94mHunt Id: 61210404295535902[0m
Active: True
Created at: 2019-11-13 16:27:45.013226

""")
    return values


def text_detele_hunts():
    values = []
    values.append(
        u"""[93mSuccessfully deleted Hunt:[0m
[94mHunt Id: 61210404295535902[0m
Active: True
Created at: 2019-11-13 16:27:45.013226

""")
    return values


def local_artifacts(paths):
    values = []
    for full_path in paths:
        path, file_name = os.path.split(full_path)
        values.append(resources.LocalArtifact(path=path, artifact_name=file_name, analyze=False))
    return values


def text_local_artifacts(path):
    values = []
    values.append(
        u"""Successfully downloaded artifact malicious to {}

""".format(path))
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


def submissions(test):
    values = []
    values.append(resources.Submission(
        {u'account_id': u'1', u'community': u'gamma', u'country': u'', u'instances': [{u'account_id': u'1', u'artifact_id': u'11611818710765483', u'assertions': [{u'author': u'0x05328f171b8c1463eaFDACCA478D9EE6a1d923F8', u'author_name': u'eicar', u'bid': u'1000000000000000000', u'engine': {u'description': u'eicar', u'name': u'eicar', u'tags': []}, u'mask': True, u'metadata': {u'malware_family': u'Eicar Test File', u'scanner': {u'environment': {u'architecture': u'x86_64', u'operating_system': u'Linux'}}}, u'verdict': True}], u'community': u'gamma', u'country': u'', u'created': u'2019-11-14T16:30:00.888191', u'extended_type': u'EICAR virus test files', u'failed': False, u'filename': u'malicious', u'first_seen': u'2019-11-01T21:33:53.292099', u'id': 56977143704899183, u'last_seen': u'2019-11-14T13:30:00.882041', u'md5': u'44d88612fea8a8f36de82e1278abb02f', u'metadata': None, u'mimetype': u'text/plain', u'result': True, u's3_file_name': u'testing/files/27/5a/02/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'sha1': u'3395856ce81f2b7382dee72602f798b642f14140', u'sha256': u'275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', u'size': 68, u'submission_id': 4563909428746367, u'submission_uuid': u'74ac1097-2477-4566-951a-bf0c2716642e', u'type': u'FILE', u'votes': [{u'arbiter': u'0xF870491ea0F53F67846Eecb57855284D8270284D', u'vote': True}], u'window_closed': True}], u'status': u'Bounty Settled', u'uuid': u'74ac1097-2477-4566-951a-bf0c2716642e'},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community=u'gamma'),
    ))
    return values


def text_submissions():
    values = []
    values.append(
        u"""[92mSubmission 74ac1097-2477-4566-951a-bf0c2716642e[0m
Reference: https://polyswarm.network/scan/results/74ac1097-2477-4566-951a-bf0c2716642e
Community: gamma
============================= Artifact Instance =============================
[92m	SHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
	SHA1: 3395856ce81f2b7382dee72602f798b642f14140
	MD5: 44d88612fea8a8f36de82e1278abb02f
	File type: mimetype: text/plain, extended_info: EICAR virus test files
	First seen: 2019-11-01T21:33:53.292099
	Filename: malicious
	PolyScore: 0.00024050482800527995
	Scan permalink: https://polyswarm.network/scan/results/74ac1097-2477-4566-951a-bf0c2716642e
[91m	Detections: 1/1 engines reported malicious[0m
[91m	eicar: Malicious, metadata: {'malware_family': 'Eicar Test File', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}[0m


""")
    return values


def scores(test):
    values = []
    values.append(resources.PolyScore(
        {u'scores': {u'56977143704899183': 0.00024050482800527995, u'11611818710765483': 0.00024050482800527995, u'49091542211453596': 0.00024050482800527995,}},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community=u'gamma'),
    ))
    return values