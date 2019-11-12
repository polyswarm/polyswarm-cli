from polyswarm_api.types import resources


def instances():
    values = []
    values.append(resources.ArtifactInstance(
        {'account_id': '1', 'artifact_id': '11611818710765483', 'assertions': [{'author': '0x05328f171b8c1463eaFDACCA478D9EE6a1d923F8', 'author_name': 'eicar', 'bid': '1000000000000000000', 'engine': {'description': 'eicar', 'name': 'eicar', 'tags': []}, 'mask': True, 'metadata': {'malware_family': 'Eicar Test File', 'scanner': {'environment': {'architecture': 'x86_64', 'operating_system': 'Linux'}}}, 'verdict': True}], 'community': 'gamma', 'country': '', 'created': '2019-11-07T19:18:00.265903', 'extended_type': 'EICAR virus test files', 'failed': False, 'filename': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'first_seen': '2019-11-01T21:33:53.292099', 'id': 49091542211453596, 'last_seen': '2019-11-07T16:18:00.269290', 'md5': '44d88612fea8a8f36de82e1278abb02f', 'metadata': None, 'mimetype': 'text/plain', 'result': True, 's3_file_name': 'testing/files/27/5a/02/275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'sha1': '3395856ce81f2b7382dee72602f798b642f14140', 'sha256': '275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f', 'size': 68, 'submission_id': 44664431668105478, 'submission_uuid': '56944690-6376-44d3-8bff-00c217ccb272', 'type': 'FILE', 'votes': [{'arbiter': '0xF870491ea0F53F67846Eecb57855284D8270284D', 'vote': True}], 'window_closed': True}
    ))
    return values


def text_instances():
    values = []
    values.append(
        """[94mFile 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
[92mFile type: mimetype: text/plain, extended_info: EICAR virus test files[0m
[92mSHA256: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
[92mSHA1: 3395856ce81f2b7382dee72602f798b642f14140[0m
[92mMD5: 44d88612fea8a8f36de82e1278abb02f[0m
[92mFirst seen: 2019-11-01T21:33:53.292099[0m
[92mFilename: 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f[0m
[92mScan permalink: https://polyswarm.network/scan/results/56944690-6376-44d3-8bff-00c217ccb272[0m
[91mDetections: 1/1 engines reported malicious[0m

"""
    )
    return values