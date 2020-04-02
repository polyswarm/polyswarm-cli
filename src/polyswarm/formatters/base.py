from __future__ import absolute_import, unicode_literals


class BaseOutput(object):
    name = 'base'

    def __init__(self, output, **kwargs):
        self.out = output

    def artifact_instance(self, result, timeout=False):
        raise NotImplementedError

    def hunt_result(self, result):
        raise NotImplementedError

    def hunt_deletion(self, result):
        raise NotImplementedError

    def hunt(self, result):
        raise NotImplementedError

    def local_artifact(self, result):
        raise NotImplementedError

    def ruleset(self, result, contents=False):
        raise NotImplementedError

    def metadata(self, result):
        raise NotImplementedError

    def tag_link(self, result):
        raise NotImplementedError

    def family(self, result):
        raise NotImplementedError

    def tag(self, result):
        raise NotImplementedError
