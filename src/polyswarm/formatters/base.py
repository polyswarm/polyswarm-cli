class BaseOutput:
    name = 'base'

    def __init__(self, output, **kwargs):
        self.out = output

    def artifact_instance(self, result, timeout=False):
        raise NotImplementedError

    def historical_result(self, result):
        raise NotImplementedError

    def hunt_deletion(self, result):
        raise NotImplementedError

    def hunt(self, result):
        raise NotImplementedError

    def local_artifact(self, result):
        raise NotImplementedError

    def ruleset(self, result, contents=False):
        raise NotImplementedError

    def iocs(self, iocs, write=True):
        raise NotImplementedError
    
    def ioc(self, iocs, write=True):
        raise NotImplementedError

    def known_host(self, iocs, write=True):
        raise NotImplementedError

    def metadata(self, result):
        raise NotImplementedError

    def tag_link(self, result):
        raise NotImplementedError

    def family(self, result):
        raise NotImplementedError

    def tag(self, result):
        raise NotImplementedError

    def artifact_metadata(self, result, only=None):
        raise NotImplementedError

    def sandbox_list(self, result):
        raise NotImplementedError

    def sandbox_task(self, result):
        raise NotImplementedError

    def sandbox_tasks(self, results):
        raise NotImplementedError
