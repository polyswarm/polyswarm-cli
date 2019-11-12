from polyswarm_api.const import USAGE_EXCEEDED_MESSAGE


class BaseOutput(object):
    name = 'base'

    def __init__(self, output, **kwargs):
        self.out = output

    def artifact_instance(self, result):
        raise NotImplementedError

    def hunt_result(self, result):
        raise NotImplementedError

    def submission(self, result):
        raise NotImplementedError

    def hunt(self, result):
        raise NotImplementedError

    def local_artifact(self, result):
        raise NotImplementedError

    @staticmethod
    def usage_exceeded():
        print(USAGE_EXCEEDED_MESSAGE)
