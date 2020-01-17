import json

from . import base


class SHA256Output(base.BaseOutput):
    """ Formatter that simply outputs SHA256s separated by newlines, only supports search/scan results """
    name = 'sha256'
    @staticmethod
    def _to_json(result):
        return json.dumps(result.json['result'])

    def artifact_instance(self, instance, timeout=False):
        self.out.write(instance.sha256 + '\n')

    def hunt_result(self, result):
        self.out.write(result.artifact.sha256 + '\n')


class SHA1Output(base.BaseOutput):
    """ Formatter that simply outputs SHA1s separated by newlines, only supports search/scan results """
    name = 'sha1'
    @staticmethod
    def _to_json(result):
        return json.dumps(result.json['result'])

    def artifact_instance(self, result, timeout=False):
        self.out.write(result.sha1 + '\n')

    def hunt_result(self, result):
        self.out.write(result.artifact.sha1 + '\n')


class MD5Output(base.BaseOutput):
    """ Formatter that simply outputs MD5s separated by newlines, only supports search/scan results """
    name = 'md5'
    @staticmethod
    def _to_json(result):
        return json.dumps(result.json['result'])

    def artifact_instance(self, result, timeout=False):
        self.out.write(result.md5 + '\n')

    def hunt_result(self, result):
        self.out.write(result.artifact.md5 + '\n')
