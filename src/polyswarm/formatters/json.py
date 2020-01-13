from __future__ import absolute_import
import json
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalTrueColorFormatter


from . import base
from polyswarm_api.const import USAGE_EXCEEDED_MESSAGE


class JSONOutput(base.BaseOutput):
    name = 'json'
    @staticmethod
    def _to_json(json_data):
        return json.dumps(json_data, sort_keys=True)

    def artifact_instance(self, result, timeout=False):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt_result(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def rule_set(self, result, contents=False):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt_deletion(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def local_artifact(self, artifact):
        self.out.write(json.dumps({'hash': artifact.artifact_name, 'path': artifact.path}, sort_keys=True)+'\n')

    def invalid_rule(self, e):
        self.out.write(json.dumps('Malformed yara file: {}'.format(e.args[0])))

    @staticmethod
    def usage_exceeded():
        return json.dumps(USAGE_EXCEEDED_MESSAGE)


class PrettyJSONOutput(base.BaseOutput):
    name = 'pretty-json'
    @staticmethod
    def _to_json(json_data):
        formatted_json = json.dumps(json_data, indent=4, sort_keys=True)
        return highlight(formatted_json, JsonLexer(), TerminalTrueColorFormatter(style='monokai'))

    def artifact_instance(self, result, timeout=False):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt_result(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def rule_set(self, result, contents=False):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt_deletion(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def local_artifact(self, artifact):
        self.out.write(json.dumps({'hash': artifact.artifact_name, 'path': artifact.path}, sort_keys=True)+'\n')

    def invalid_rule(self, e):
        self.out.write(json.dumps('Malformed yara file: {}'.format(e.args[0])))

    @staticmethod
    def usage_exceeded():
        return json.dumps(USAGE_EXCEEDED_MESSAGE)
