from __future__ import absolute_import, unicode_literals
import json

import click
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter


from polyswarm.formatters import base


class JSONOutput(base.BaseOutput):
    name = 'json'
    @staticmethod
    def _to_json(json_data):
        return json.dumps(json_data, sort_keys=True)

    def artifact_instance(self, result, timeout=False):
        click.secho(self._to_json(result.json), file=self.out)

    def hunt_result(self, result):
        click.secho(self._to_json(result.json), file=self.out)

    def hunt_deletion(self, result):
        click.secho(self._to_json(result.json), file=self.out)

    def hunt(self, result):
        click.secho(self._to_json(result.json), file=self.out)

    def local_artifact(self, artifact):
        click.secho(
            json.dumps({'hash': artifact.artifact_name, 'path': artifact.path}, sort_keys=True),
            file=self.out,
        )

    def ruleset(self, result, contents=False):
        click.secho(self._to_json(result.json), file=self.out)

    def metadata(self, result):
        click.secho(self._to_json(result.json), file=self.out)

    def tag_link(self, result):
        click.secho(self._to_json(result.json), file=self.out)

    def family(self, result):
        click.secho(self._to_json(result.json), file=self.out)

    def tag(self, result):
        click.secho(self._to_json(result.json), file=self.out)


class PrettyJSONOutput(JSONOutput):
    name = 'pretty-json'

    def __init__(self, output, color, **kwargs):
        super(PrettyJSONOutput, self).__init__(output, **kwargs)
        self.color = color

    def _to_json(self, json_data):
        formatted_json = json.dumps(json_data, indent=4, sort_keys=True)
        if not self.color:
            return formatted_json
        return highlight(formatted_json, JsonLexer(), Terminal256Formatter(style='monokai'))
