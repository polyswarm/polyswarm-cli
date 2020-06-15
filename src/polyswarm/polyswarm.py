from __future__ import absolute_import
import logging

from polyswarm_api.api import PolyswarmAPI
from polyswarm_api import const

from polyswarm import utils


logger = logging.getLogger(__name__)


def submit_and_wait(api, timeout, nowait, *args, **kwargs):
    instance = api.submit(*args, **kwargs)
    if nowait:
        return instance
    return api.wait_for(instance.id, timeout=timeout)


def rescan_and_wait(api, timeout, nowait, *args, **kwargs):
    instance = api.rescan(*args, **kwargs)
    if nowait:
        return instance
    return api.wait_for(instance.id, timeout=timeout)


def rescan_id_and_wait(api, timeout, nowait, *args, **kwargs):
    instance = api.rescan_id(*args, **kwargs)
    if nowait:
        return instance
    return api.wait_for(instance.id, timeout=timeout)


class Polyswarm(PolyswarmAPI):
    def __init__(self, *args, **kwargs):
        # signature should be __init__(self, *args, parallel=None, **kwargs), but python 2 does not like it
        parallel = kwargs.pop('parallel', None)
        super(Polyswarm, self).__init__(*args, **kwargs)
        self.parallel = parallel

    def scan_file(self, path, recursive=False, timeout=const.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config=None):
        args = [(self, timeout, nowait, file) for file in utils.collect_files(path, recursive=recursive)]
        for instance in utils.parallel_executor(submit_and_wait,
                                                args_list=args,
                                                kwargs_list=[{'scan_config': scan_config}]*len(args)):
            yield instance

    def scan_url(self, urls, timeout=const.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config='more-time'):
        args = [(self, timeout, nowait, url) for url in urls]
        kwargs = [dict(artifact_type='url', scan_config=scan_config) for _ in urls]

        for instance in utils.parallel_executor(submit_and_wait, args_list=args, kwargs_list=kwargs):
            yield instance

    def scan_rescan(self, values, hash_type=None, timeout=const.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config=None):
        args = [(self, timeout, nowait, h) for h in values]

        for instance in utils.parallel_executor(rescan_and_wait,
                                                args_list=args,
                                                kwargs_list=[{'hash_type': hash_type,
                                                              'scan_config': scan_config}]*len(args)):
            yield instance

    def scan_rescan_id(self, scan_id, timeout=const.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config=None):
        args = [(self, timeout, nowait, s) for s in scan_id]
        kwargs = [dict(scan_config=scan_config) for _ in scan_id]

        for instance in utils.parallel_executor(rescan_id_and_wait, args_list=args, kwargs_list=kwargs):
            yield instance

    def scan_lookup(self, scan_ids):
        for result in utils.parallel_executor(self.lookup, args_list=[(u,) for u in scan_ids]):
            yield result

    def scan_wait(self, scan_id, timeout=const.DEFAULT_SCAN_TIMEOUT):
        args = [(s,) for s in scan_id]
        kwargs = [dict(timeout=timeout)]*len(args)

        for result in utils.parallel_executor(self.wait_for, args_list=args, kwargs_list=kwargs):
            yield result

    def search_hashes(self, values, hash_type=None):
        args = [(h,) for h in values]
        for instance in utils.parallel_executor_iterable_results(self.search, args_list=args,
                                                                 kwargs_list=[{'hash_type': hash_type}]*len(args)):
            yield instance

    def search_urls(self, url):
        args = [(u,) for u in url]
        for instance in utils.parallel_executor_iterable_results(self.search_url, args_list=args):
            yield instance

    def download_multiple(self, values, destination, hash_type=None):
        args = [(destination, h) for h in values]

        for result in utils.parallel_executor(self.download, args_list=args,
                                              kwargs_list=[{'hash_type': hash_type}]*len(args)):
            yield result

    def download_stream(self, destination, since=1440):
        args = [(destination, artifact_archive.uri) for artifact_archive in self.stream(since=since)]
        for result in utils.parallel_executor(self.download_archive, args_list=args):
            yield result

    def live_start(self, hunt_id):
        kwargs = [dict(hunt=h) for h in hunt_id]
        args = [(True,)]*len(kwargs)
        for result in utils.parallel_executor(self.live_update, args_list=args, kwargs_list=kwargs):
            yield result

    def live_stop(self, hunt_id):
        kwargs = [dict(hunt=h) for h in hunt_id] if hunt_id else [dict(hunt_id=None)]
        args = [(False,)] * len(kwargs)
        for result in utils.parallel_executor(self.live_update, args_list=args, kwargs_list=kwargs):
            yield result

    def live_delete_multiple(self, hunt_id):
        kwargs = [dict(hunt=h) for h in hunt_id]
        for result in utils.parallel_executor(self.live_delete, kwargs_list=kwargs):
            yield result

    def live_results_multiple(self, hunt_id, since=1440, tag=None, rule_name=None):
        args = [(h,) for h in hunt_id] if hunt_id else [(None,)]
        kwargs = [dict(since=since, tag=tag, rule_name=rule_name)]*len(args)
        for result in utils.parallel_executor_iterable_results(self.live_results, args_list=args, kwargs_list=kwargs):
            yield result

    def historical_delete_multiple(self, hunt_id):
        kwargs = [dict(hunt=h) for h in hunt_id]
        for result in utils.parallel_executor(self.historical_delete, kwargs_list=kwargs):
            yield result

    def historical_results_multiple(self, hunt_id, tag=None, rule_name=None):
        args = [(h,) for h in hunt_id] if hunt_id else [(None,)]
        kwargs = [dict(tag=tag, rule_name=rule_name)] * len(args)
        for result in utils.parallel_executor_iterable_results(self.historical_results, args_list=args, kwargs_list=kwargs):
            yield result

