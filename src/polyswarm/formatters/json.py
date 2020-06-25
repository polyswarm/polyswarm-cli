from __future__ import absolute_import, unicode_literals
import json

import click
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter

from polyswarm.formatters import base


class ClickFormatter(Terminal256Formatter):
    def format_unencoded(self, tokensource, outfile):
        # https://github.com/pygments/pygments/blob/35544e2fc6eed0ce4a27ec7285aac71ff0ddc473/pygments/formatters/terminal256.py#L244
        for ttype, value in tokensource:
            not_found = True
            while ttype and not_found:
                try:
                    on, off = self.style_string[str(ttype)]
                    spl = value.split('\n')
                    for line in spl[:-1]:
                        if line:
                            click.echo(on + line + off, file=outfile, nl=False)
                        outfile.write('\n')
                    if spl[-1]:
                        click.echo(on + spl[-1] + off, file=outfile, nl=False)
                    not_found = False
                except KeyError:
                    ttype = ttype[:-1]
            if not_found:
                click.echo(value, file=outfile, nl=False)


class JSONOutput(base.BaseOutput):
    name = 'json'
    @staticmethod
    def _to_json(json_data):
        return json.dumps(json_data, sort_keys=True)

    def artifact_instance(self, result, timeout=False):
        click.echo(self._to_json(result.json), file=self.out)

    def hunt_result(self, result):
        click.echo(self._to_json(result.json), file=self.out)

    def hunt_deletion(self, result):
        click.echo(self._to_json(result.json), file=self.out)

    def hunt(self, result):
        click.echo(self._to_json(result.json), file=self.out)

    def local_artifact(self, artifact):
        click.echo(
            json.dumps({'hash': artifact.artifact_name, 'path': artifact.path}, sort_keys=True),
            file=self.out,
        )

    def ruleset(self, result, contents=False):
        click.echo(self._to_json(result.json), file=self.out)

    def metadata(self, result):
        click.echo(self._to_json(result.json), file=self.out)

    def tag_link(self, result):
        click.echo(self._to_json(result.json), file=self.out)

    def family(self, result):
        click.echo(self._to_json(result.json), file=self.out)

    def tag(self, result):
        click.echo(self._to_json(result.json), file=self.out)


class PrettyJSONOutput(JSONOutput):
    name = 'pretty-json'

    def __init__(self, output, color, **kwargs):
        super(PrettyJSONOutput, self).__init__(output, **kwargs)
        self.color = color

    def _to_json(self, json_data):
        formatted_json = json.dumps(json_data, indent=4, sort_keys=True)
        if not self.color:
            return formatted_json
        return highlight(formatted_json, JsonLexer(), ClickFormatter(style='monokai'), outfile=self.out)
