import json as json_

from . import base
from polyswarm_api.const import USAGE_EXCEEDED_MESSAGE


class JSONOutput(base.BaseOutput):
    name = 'json'
    @staticmethod
    def _to_json(json_data):
        return json_.dumps(json_data, sort_keys=True)

    def artifact_instance(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def submission(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt_result(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt_deletion(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def local_artifact(self, artifact):
        self.out.write(json_.dumps({'hash': artifact.artifact_name, 'path': artifact.path}, sort_keys=True)+'\n')

    def invalid_rule(self, e):
        self.out.write(json_.dumps('Malformed yara file: {}'.format(e.args[0])))

    @staticmethod
    def usage_exceeded():
        return json_.dumps(USAGE_EXCEEDED_MESSAGE)


class PrettyJSONOutput(base.BaseOutput):
    name = 'pretty-json'
    @staticmethod
    def _to_json(json_data):
        return json_.dumps(json_data, indent=4, sort_keys=True)

    def artifact_instance(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def submission(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt_result(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def hunt_deletion(self, result):
        self.out.write(self._to_json(result.json) + '\n')

    def local_artifact(self, artifact):
        self.out.write(json_.dumps({'hash': artifact.artifact_name, 'path': artifact.path}, sort_keys=True)+'\n')

    def invalid_rule(self, e):
        self.out.write(json_.dumps('Malformed yara file: {}'.format(e.args[0])))

    @staticmethod
    def usage_exceeded():
        return json_.dumps(USAGE_EXCEEDED_MESSAGE)
