from __future__ import absolute_import, unicode_literals
import json

import click
from click import termui
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter
from pygments.formatters.terminal256 import EscapeSequence


from polyswarm.formatters import base


class ClickFormatter(Terminal256Formatter):
    name = 'ClickFormatter'
    aliases = ['click']
    _reverse_color = {v: k for k, v in termui._ansi_colors.items()}

    def _closest_color(self, r, g, b):
        distance = 257*257*3  # "infinity" (>distance from #000000 to #ffffff)
        match = 0

        for i in range(0, 15):
            values = self.xterm_colors[i]

            rd = r - values[0]
            gd = g - values[1]
            bd = b - values[2]
            d = rd*rd + gd*gd + bd*bd

            if d < distance:
                match = i
                distance = d
        if match < 8:
            match += 30
        else:
            match += 82
        return self._reverse_color[match]

    def _setup_styles(self):
        for ttype, ndef in self.style:
            # set to None instead of False by default, this avoids
            # adding needless extra codes in click.style()
            escape = EscapeSequence(bold=None, underline=None)
            # get foreground from ansicolor if set
            if ndef['ansicolor']:
                escape.fg = self._color_index(ndef['ansicolor'])
            elif ndef['color']:
                escape.fg = self._color_index(ndef['color'])
            if ndef['bgansicolor']:
                escape.bg = self._color_index(ndef['bgansicolor'])
            elif ndef['bgcolor']:
                escape.bg = self._color_index(ndef['bgcolor'])
            if self.usebold and ndef['bold']:
                escape.bold = True
            if self.useunderline and ndef['underline']:
                escape.underline = True
            self.style_string[str(ttype)] = escape

    def format_unencoded(self, tokensource, outfile):
        for ttype, value in tokensource:
            not_found = True
            while ttype and not_found:
                try:
                    escape = self.style_string[str(ttype)]
                    spl = value.split('\n')
                    for line in spl[:-1]:
                        if line:
                            click.secho(line, file=outfile, nl=False, fg=escape.fg,
                                        bg=escape.bg, bold=escape.bold, underline=escape.underline)
                        click.secho('', file=outfile)
                    if spl[-1]:
                        click.secho(spl[-1], file=outfile, nl=False, fg=escape.fg,
                                    bg=escape.bg, bold=escape.bold, underline=escape.underline)
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
            json.dumps({'artifact_name': artifact.artifact_name, 'path': artifact.name}, sort_keys=True),
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

    def mapping(self, result):
        click.echo(self._to_json(result.json), file=self.out)

    def assertions(self, result):
        click.echo(self._to_json(result.json), file=self.out)

    def votes(self, result):
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
