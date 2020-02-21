from __future__ import absolute_import, unicode_literals
import logging
import json

from . import base


logger = logging.getLogger(__name__)


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

    def metadata(self, result):
        if result.sha256:
            self.out.write(result.sha256 + '\n')
        else:
            logger.warning('Could not render metadata as sha256, value is %s', result.sha256)


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

    def metadata(self, result):
        if result.sha1:
            self.out.write(result.sha1 + '\n')
        else:
            logger.warning('Could not render metadata as sha1, value is %s', result.sha1)


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

    def metadata(self, result):
        if result.md5:
            self.out.write(result.md5 + '\n')
        else:
            logger.warning('Could not render metadata as md5, value is %s', result.md5)
