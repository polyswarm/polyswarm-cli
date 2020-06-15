import logging

from polyswarm_api.api import PolyswarmAPI

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


class Polyswarm:
    def __init__(self, api_key, uri=None, community=None,
                 validate_schemas=None, parallel=None):
        self.api = PolyswarmAPI(api_key, uri=uri, community=community, validate_schemas=validate_schemas)
        self.parallel = parallel

    def scan_file(self, recursive, timeout, nowait, path, scan_config):
        args = [(self.api, timeout, nowait, file) for file in utils.collect_files(path, recursive=recursive)]
        for instance in utils.parallel_executor(submit_and_wait,
                                                args_list=args,
                                                kwargs_list=[{'scan_config': scan_config}]*len(args)):
            yield instance

    def scan_url(self, url_file, timeout, nowait, url, scan_config):
        urls = list(url)
        if url_file:
            urls.extend([u.strip() for u in url_file.readlines()])
        args = [(self.api, timeout, nowait, url) for url in urls]
        kwargs = [dict(artifact_type='url', scan_config=scan_config) for _ in urls]

        for instance in utils.parallel_executor(submit_and_wait, args_list=args, kwargs_list=kwargs):
            yield instance

    def scan_rescan(self, hash_file, hash_type, timeout, nowait, hash_value, scan_config):
        args = [(self.api, timeout, nowait, h) for h in utils.parse_hashes(hash_value, hash_file=hash_file)]

        for instance in utils.parallel_executor(rescan_and_wait,
                                                args_list=args,
                                                kwargs_list=[{'hash_type': hash_type,
                                                              'scan_config': scan_config}]*len(args)):
            yield instance

    def scan_rescan_id(self, timeout, nowait, scan_id, scan_config):
        args = [(self.api, timeout, nowait, s) for s in scan_id]
        kwargs = [dict(scan_config=scan_config) for _ in scan_id]

        for instance in utils.parallel_executor(rescan_id_and_wait, args_list=args, kwargs_list=kwargs):
            yield instance

    def scan_lookup(self, scan_id, scan_id_file):
        scan_ids = list(scan_id)

        # TODO dedupe
        if scan_id_file:
            for u in scan_id_file.readlines():
                u = u.strip()
                if utils.is_valid_id(u):
                    scan_ids.append(u)
                else:
                    logger.warning('Invalid scan id %s in file, ignoring.', u)

        for result in utils.parallel_executor(self.api.lookup, args_list=[(u,) for u in scan_ids]):
            yield result

    def scan_wait(self, scan_id, timeout):
        args = [(s,) for s in scan_id]
        kwargs = [dict(timeout=timeout)]*len(args)

        for result in utils.parallel_executor(self.api.wait_for, args_list=args, kwargs_list=kwargs):
            yield result
