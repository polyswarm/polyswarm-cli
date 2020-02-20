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
         'extended_type': 'EICAR virus test files', 'polyscore': 0.5, 'failed': False,
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
Scan permalink: https://polyswarm.network/scan/results/file/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
[91mDetections: 1/1 engines reported malicious[0m
[91m	eicar[0m: Malicious, metadata: {"malware_family": "Eicar Test File", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}}}
[94mScan id: 49091542211453596[0m
[94mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01 21:33:53.292099
Last seen: 2019-11-07 16:18:00.269290
Status: Assertion window closed
Filename: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
Community: gamma
Country: 
[91mPolyScore: 0.50000000000000000000[0m

""")
    return values


def metadata(test):
    values = []
    values.append(resources.Metadata(
        {'artifact': {'created': '2020-01-14T17:48:55.854940+00:00', 'id': 19021969312842541},
         'hash': {'md5': '44d88612fea8a8f36de82e1278abb02f', 'sha1': '3395856ce81f2b7382dee72602f798b642f14140',
                  'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f',
                  'sha3_256': '8b4c4e204a8a039198e292d2291f4c451d80e4c38bf0cc04ad3841fea8755bd8',
                  'sha3_512': 'a20290c6ebf01dc5182bb57718250f61ab11b418466714632a7d1474a02849641f7b78e4093e19ad12fdbedbe02f3bec4ca3ec3235557e82ab5ac02d061e7007',
                  'sha512': 'cc805d5fab1fd71a4ab352a9c533e65fb2d5b885518f4e565e68847223b8e6b85cb48f3afad842726d99239c9e36505c64b0dc9a061d9e507d833277ada336ab',
                  'ssdeep': '3:a+JraNvsgzsVqSwHq9:tJuOgzsko', 'ssdeep_chunk': 'a+JraNvsgzsVqSwHq9',
                  'ssdeep_chunk_size': 3, 'ssdeep_double_chunk': 'tJuOgzsko',
                  'tlsh': '41a022003b0eee2ba20b00200032e8b00808020e2ce00a3820a020b8c83308803ec228',
                  'tlsh_quartiles': ['0:0', '1:0', '2:0', '3:0', '4:0', '5:3', '6:2', '7:3', '8:0', '9:0', '10:3',
                                     '11:2', '12:3', '13:2', '14:3', '15:2', '16:0', '17:2', '18:2', '19:3', '20:2',
                                     '21:2', '22:0', '23:2', '24:0', '25:0', '26:2', '27:3', '28:0', '29:0', '30:0',
                                     '31:0', '32:0', '33:2', '34:0', '35:0', '36:0', '37:0', '38:0', '39:0', '40:0',
                                     '41:3', '42:0', '43:2', '44:3', '45:2', '46:2', '47:0', '48:2', '49:3', '50:0',
                                     '51:0', '52:0', '53:0', '54:2', '55:0', '56:0', '57:0', '58:2', '59:0', '60:0',
                                     '61:0', '62:0', '63:2', '64:0', '65:0', '66:3', '67:2', '68:0', '69:2', '70:3',
                                     '71:0', '72:3', '73:2', '74:0', '75:0', '76:0', '77:0', '78:2', '79:2', '80:0',
                                     '81:3', '82:2', '83:0', '84:0', '85:2', '86:0', '87:0', '88:2', '89:2', '90:0',
                                     '91:0', '92:0', '93:2', '94:0', '95:0', '96:2', '97:3', '98:2', '99:0', '100:3',
                                     '101:0', '102:2', '103:0', '104:0', '105:3', '106:0', '107:3', '108:0', '109:0',
                                     '110:2', '111:0', '112:2', '113:0', '114:0', '115:0', '116:0', '117:3', '118:3',
                                     '119:2', '120:3', '121:0', '122:0', '123:2', '124:0', '125:2', '126:2', '127:0'],
                  'tlsh_quartiles_minimum_match': 32},
         'scan': {'countries': [], 'detections': {'malicious': 102, 'total': 102},
                  'filename': ['malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious',
                               'malicious', 'malicious', 'malicious', 'malicious', 'malicious', 'malicious'],
                  'first_scan': {'artifact_instance_id': 67493245269173378, 'eicar': {'assertion': 'malicious',
                                                                                      'metadata': {
                                                                                          'malware_family': 'Eicar Test File',
                                                                                          'scanner': {'environment': {
                                                                                              'architecture': 'x86_64',
                                                                                              'operating_system': 'Linux'}}}}},
                  'first_seen': '2020-01-14T17:48:55.854940+00:00', 'last_seen': '2020-01-16T20:41:30.953689+00:00',
                  'latest_scan': {'artifact_instance_id': 67608711919932715, 'eicar': {'assertion': 'malicious',
                                                                                       'metadata': {
                                                                                           'malware_family': 'Eicar Test File',
                                                                                           'scanner': {'environment': {
                                                                                               'architecture': 'x86_64',
                                                                                               'operating_system': 'Linux'}}}}},
                  'mimetype': {'extended': 'EICAR virus test files', 'mime': 'text/plain'}},
         'strings': {'domains': [], 'ipv4': [], 'ipv6': [], 'urls': []}},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def text_metadata():
    values = []
    values.append(
        """============================= Metadata =============================
[94mArtifact id: 19021969312842541[0m
Created: 2020-01-14 17:48:55.854940+00:00
SHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
SSDEEP: 3:a+JraNvsgzsVqSwHq9:tJuOgzsko
TLSH: 41a022003b0eee2ba20b00200032e8b00808020e2ce00a3820a020b8c83308803ec228
First seen: 2020-01-14 17:48:55.854940+00:00
Last seen: 2020-01-16 20:41:30.953689+00:00
Mimetype: text/plain
Extended mimetype: 41a022003b0eee2ba20b00200032e8b00808020e2ce00a3820a020b8c83308803ec228
Detections: 102
Total detections: 102

"""
    )
    return values


def live_results(test):
    values = []
    values.append(resources.HuntResult(
        {'artifact': {'account_id': '1', 'artifact_id': '11611818710765483', 'assertions': [
            {'author': '0x05328f171b8c1463eaFDACCA478D9EE6a1d923F8', 'author_name': 'eicar',
             'bid': '1000000000000000000', 'engine': {'description': 'eicar', 'name': 'eicar', 'tags': []},
             'mask': True, 'metadata': {'malware_family': 'Eicar Test File', 'scanner': {
                'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}, 'verdict': True}],
                      'community': 'gamma', 'country': '', 'created': '2019-11-07T19:18:00.265903',
                      'extended_type': 'EICAR virus test files', 'polyscore': 0.5, 'failed': False,
                      'filename': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f',
                      'first_seen': '2019-11-01T21:33:53.292099', 'id': 49091542211453596, 'last_seen': '2019-11-07T16:18:00.269290',
                      'md5': '44d88612fea8a8f36de82e1278abb02f', 'metadata': None, 'mimetype': 'text/plain', 'result': True,
                      's3_file_name': 'testing/files/27/5a/02/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f',
                      'sha1': '3395856ce81f2b7382dee72602f798b642f14140',
                      'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'size': 68, 'type': 'FILE',
                      'votes': [{'arbiter': '0xF870491ea0F53F67846Eecb57855284D8270284D', 'vote': True}], 'window_closed': True},
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
============================= Artifact Instance =============================
Scan permalink: https://polyswarm.network/scan/results/file/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
[91mDetections: 1/1 engines reported malicious[0m
[91m	eicar[0m: Malicious, metadata: {"malware_family": "Eicar Test File", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}}}
[94mScan id: 49091542211453596[0m
[94mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01 21:33:53.292099
Last seen: 2019-11-07 16:18:00.269290
Status: Assertion window closed
Filename: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
Community: gamma
Country: 
[91mPolyScore: 0.50000000000000000000[0m

""")
    return values


def historical_results(test):
    values = []
    values.append(resources.HuntResult(
        {'artifact': {'account_id': '1', 'artifact_id': '11611818710765483', 'assertions': [
            {'author': '0x05328f171b8c1463eaFDACCA478D9EE6a1d923F8', 'author_name': 'eicar',
             'bid': '1000000000000000000', 'engine': {'description': 'eicar', 'name': 'eicar', 'tags': []},
             'mask': True, 'metadata': {'malware_family': 'Eicar Test File', 'scanner': {
                'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}, 'verdict': True}],
                      'community': 'gamma', 'country': '', 'created': '2019-11-07T19:18:00.265903',
                      'extended_type': 'EICAR virus test files', 'polyscore': 0.5, 'failed': False,
                      'filename': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f',
                      'first_seen': '2019-11-01T21:33:53.292099', 'id': 49091542211453596, 'last_seen': '2019-11-07T16:18:00.269290',
                      'md5': '44d88612fea8a8f36de82e1278abb02f', 'metadata': None, 'mimetype': 'text/plain', 'result': True,
                      's3_file_name': 'testing/files/27/5a/02/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f',
                      'sha1': '3395856ce81f2b7382dee72602f798b642f14140',
                      'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'size': 68, 'type': 'FILE',
                      'votes': [{'arbiter': '0xF870491ea0F53F67846Eecb57855284D8270284D', 'vote': True}], 'window_closed': True},
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
============================= Artifact Instance =============================
Scan permalink: https://polyswarm.network/scan/results/file/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
[91mDetections: 1/1 engines reported malicious[0m
[91m	eicar[0m: Malicious, metadata: {"malware_family": "Eicar Test File", "scanner": {"environment": {"architecture": "x86_64", "operating_system": "Linux"}}}
[94mScan id: 49091542211453596[0m
[94mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
SHA1: 3395856ce81f2b7382dee72602f798b642f14140
MD5: 44d88612fea8a8f36de82e1278abb02f
File type: mimetype: text/plain, extended_info: EICAR virus test files
First seen: 2019-11-01 21:33:53.292099
Last seen: 2019-11-07 16:18:00.269290
Status: Assertion window closed
Filename: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
Community: gamma
Country: 
[91mPolyScore: 0.50000000000000000000[0m

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


def ruleset(test, name='test'):
    values = []
    values.append(resources.YaraRuleset(
        {'account_id': '1', 'created': '2019-11-13T16:27:45.013226', 'deleted': False, 'description': None, 'id': '67713199207380968', 'modified': '2019-11-13T16:27:45.013226', 'name': name, 'yara': 'rule eicar_av_test {\n    /*\n       Per standard, match only if entire file is EICAR string plus optional trailing whitespace.\n       The raw EICAR string to be matched is:\n       X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*\n    */\n\n    meta:\n        description = "This is a standard AV test, intended to verify that BinaryAlert is working correctly."\n        author = "Austin Byers | Airbnb CSIRT"\n        reference = "http://www.eicar.org/86-0-Intended-use.html"\n\n    strings:\n        $eicar_regex = /^X5O!P%@AP\\[4\\\\PZX54\\(P\\^\\)7CC\\)7\\}\\$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!\\$H\\+H\\*\\s*$/\n\n    condition:\n        all of them\n}\n\nrule eicar_substring_test {\n    /*\n       More generic - match just the embedded EICAR string (e.g. in packed executables, PDFs, etc)\n    */\n\n    meta:\n        description = "Standard AV test, checking for an EICAR substring"\n        author = "Austin Byers | Airbnb CSIRT"\n\n    strings:\n        $eicar_substring = "$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!"\n\n    condition:\n        all of them\n}'},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def artifact_archives(test):
    values = []
    values.append(resources.ArtifactArchive(
        {'id': '1', 'community': 'gamma', 'created': '2019-11-14T16:30:00.888191', 'uri': 's3/malicious'},
        polyswarm=PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma'),
    ))
    return values


def local_artifacts(test, path, files):
    file_paths = [os.path.join(path, file_name) for file_name in files]
    api = PolyswarmAPI(test.test_api_key, uri=test.api_url, community='gamma')
    values = [resources.LocalArtifact.from_path(api, full_path) for full_path in file_paths]
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


def stream_results(s3_file_url):
    values = []
    values.append(
        {'community': 'gamma', 'created': '2019-11-28T18:04:38.923000',
         'id': '67497956521144077',
         'uri': s3_file_url})
    return values
