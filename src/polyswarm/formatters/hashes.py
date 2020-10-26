from __future__ import absolute_import, unicode_literals
import logging
import json

import click

from polyswarm.formatters import base


logger = logging.getLogger(__name__)


class SHA256Output(base.BaseOutput):
    """ Formatter that simply outputs SHA256s separated by newlines, only supports search/scan results """
    name = 'sha256'
    @staticmethod
    def _to_json(result):
        return json.dumps(result.json['result'])

    def artifact_instance(self, instance, timeout=False):
        click.echo(instance.sha256, file=self.out)

    def hunt_result(self, result):
        click.echo(result.artifact.sha256, file=self.out)

    def tag_link(self, result):
        click.echo(result.sha256, file=self.out)

    def metadata(self, result):
        if result.sha256:
            click.echo(result.sha256, file=self.out)
        else:
            logger.warning('Could not render metadata as sha256, value is %s', result.sha256)


class SHA1Output(base.BaseOutput):
    """ Formatter that simply outputs SHA1s separated by newlines, only supports search/scan results """
    name = 'sha1'
    @staticmethod
    def _to_json(result):
        return json.dumps(result.json['result'])

    def artifact_instance(self, result, timeout=False):
        click.echo(result.sha1, file=self.out)

    def hunt_result(self, result):
        click.echo(result.artifact.sha1, file=self.out)

    def metadata(self, result):
        if result.sha1:
            click.echo(result.sha1, file=self.out)
        else:
            logger.warning('Could not render metadata as sha1, value is %s', result.sha1)


class MD5Output(base.BaseOutput):
    """ Formatter that simply outputs MD5s separated by newlines, only supports search/scan results """
    name = 'md5'
    @staticmethod
    def _to_json(result):
        return json.dumps(result.json['result'])

    def artifact_instance(self, result, timeout=False):
        click.echo(result.md5, file=self.out)

    def hunt_result(self, result):
        click.echo(result.artifact.md5, file=self.out)

    def metadata(self, result):
        if result.md5:
            click.echo(result.md5, file=self.out)
        else:
            logger.warning('Could not render metadata as md5, value is %s', result.md5)
