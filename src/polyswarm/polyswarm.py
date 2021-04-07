from __future__ import absolute_import
import logging

from polyswarm_api.api import PolyswarmAPI
from polyswarm_api import settings

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

    def scan_file(self, path, recursive=False, timeout=settings.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config=None):
        """
        Scan files or directories via PolySwarm.

        :param path: A list of paths for files or directories.
        :param recursive: Scan directories recursively.
        :param timeout: How long to wait for results.
        :param nowait: Does not wait for the scan window to close, just create it and return right away.
        :param scan_config: Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".
        :return: An iterator of artifact instances.
        """
        args = [(self, timeout, nowait, file) for file in utils.collect_files(path, recursive=recursive)]
        for instance in utils.parallel_executor(submit_and_wait,
                                                args_list=args,
                                                kwargs_list=[{'scan_config': scan_config}]*len(args)):
            yield instance

    def scan_url(self, urls, timeout=settings.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config='more-time'):
        """
        Scan files or directories via PolySwarm

        :param urls: A list of urls.
        :param timeout: How long to wait for results.
        :param nowait: Does not wait for the scan window to close, just create it and return right away.
        :param scan_config: Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".
        :return: An iterator of artifact instances.
        """
        args = [(self, timeout, nowait, url) for url in urls]
        kwargs = [dict(artifact_type='url', scan_config=scan_config) for _ in urls]

        for instance in utils.parallel_executor(submit_and_wait, args_list=args, kwargs_list=kwargs):
            yield instance

    def scan_rescan(self, hashes, hash_type=None, timeout=settings.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config=None):
        """
        Rescan files with matched hashes.

        :param hashes: A list of hashes to rescan.
        :param hash_type: Hash type to search [default:autodetect, sha256|sha1|md5].
        :param timeout: How long to wait for results.
        :param nowait: Does not wait for the scan window to close, just create it and return right away.
        :param scan_config: Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".
        :return: An iterator of artifact instances.
        """
        args = [(self, timeout, nowait, h) for h in hashes]

        for instance in utils.parallel_executor(rescan_and_wait,
                                                args_list=args,
                                                kwargs_list=[{'hash_type': hash_type,
                                                              'scan_config': scan_config}]*len(args)):
            yield instance

    def scan_rescan_id(self, scan_id, timeout=settings.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config=None):
        """
        Rescan based on the id of a previous scan.

        :param scan_id: Id of the artifact to be re-scanned.
        :param timeout: How long to wait for results.
        :param nowait: Does not wait for the scan window to close, just create it and return right away.
        :param scan_config: Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".
        :return: An iterator of artifact instances.
        """
        args = [(self, timeout, nowait, s) for s in scan_id]
        kwargs = [dict(scan_config=scan_config) for _ in scan_id]

        for instance in utils.parallel_executor(rescan_id_and_wait, args_list=args, kwargs_list=kwargs):
            yield instance

    def scan_lookup(self, scan_ids):
        """
        Lookup a PolySwarm scan by Scan id for current status.

        :param scan_ids: List of ids to lookup.
        :return: An iterator of artifact instances.
        """
        for result in utils.parallel_executor(self.lookup, args_list=[(u,) for u in scan_ids]):
            yield result

    def scan_wait(self, scan_id, timeout=settings.DEFAULT_SCAN_TIMEOUT):
        """
        Lookup a PolySwarm scan by Scan id for current status and wait for it to finish if not done.

        :param scan_id: List of ids to wait.
        :param timeout: How long to wait for results.
        :return: An iterator of artifact instances.
        """
        args = [(s,) for s in scan_id]
        kwargs = [dict(timeout=timeout)]*len(args)

        for result in utils.parallel_executor(self.wait_for, args_list=args, kwargs_list=kwargs):
            yield result

    def search_hashes(self, hashes, hash_type=None):
        """
        Search PolySwarm for files matching hashes.

        :param hashes: List of hashes to search.
        :param hash_type: Hash type to search.
        :return: An iterator of artifact instances.
        """
        args = [(h,) for h in hashes]
        for instance in utils.parallel_executor_iterable_results(self.search, args_list=args,
                                                                 kwargs_list=[{'hash_type': hash_type}]*len(args)):
            yield instance

    def search_urls(self, url):
        """
        Search PolySwarm for a scan matching the url.

        :param url: List of urls to search.
        :return: An iterator of artifact instances.
        """
        args = [(u,) for u in url]
        for instance in utils.parallel_executor_iterable_results(self.search_url, args_list=args):
            yield instance

    def download_multiple(self, hashes, destination, hash_type=None):
        """
        Download files from matching hashes.

        :param hashes: A list of hashes to download.
        :param destination: Folder where to download the files to.
        :param hash_type: Hash type to search.
        :return: An iterator of local artifacts.
        """
        args = [(destination, h) for h in hashes]

        for result in utils.parallel_executor(self.download, args_list=args,
                                              kwargs_list=[{'hash_type': hash_type}]*len(args)):
            yield result

    def download_stream(self, destination, since=1440):
        """
        Access the polyswarm file stream.

        :param destination: Folder where to download the files to.
        :param since: Request archives X minutes into the past. Default: 1440, Max: 2880.
        :return: An iterator of local artifacts.
        """
        args = [(destination, artifact_archive.uri) for artifact_archive in self.stream(since=since)]
        for result in utils.parallel_executor(self.download_archive, args_list=args):
            yield result

    def live_start(self, hunt_id):
        """
        Start an existing live hunt.

        :param hunt_id: List of hunt ids.
        :return: An iterator of hunt objects.
        """
        kwargs = [dict(hunt=h) for h in hunt_id]
        args = [(True,)]*len(kwargs)
        for result in utils.parallel_executor(self.live_update, args_list=args, kwargs_list=kwargs):
            yield result

    def live_stop(self, hunt_id):
        """
        Stop an existing live hunt.

        :param hunt_id: List of hunt ids.
        :return: An iterator of hunt objects.
        """
        kwargs = [dict(hunt=h) for h in hunt_id] if hunt_id else [dict(hunt=None)]
        args = [(False,)] * len(kwargs)
        for result in utils.parallel_executor(self.live_update, args_list=args, kwargs_list=kwargs):
            yield result

    def live_delete_multiple(self, hunt_id):
        """
        Delete the live hunt associated with the given hunt_id.

        :param hunt_id: List of hunt ids.
        :return: An iterator of hunt objects.
        """
        kwargs = [dict(hunt=h) for h in hunt_id]
        for result in utils.parallel_executor(self.live_delete, kwargs_list=kwargs):
            yield result

    def live_results_multiple(self, hunt_id, since=1440, tag=None, rule_name=None):
        """
        Get results from live hunt.

        :param hunt_id: List of hunt ids.
        :param since: How far back in seconds to request results (default: 1440).
        :param tag: Filter results on this tag.
        :param rule_name: Filter results on this rule name.
        :return: An iterator of hunt objects.
        """
        args = [(h,) for h in hunt_id] if hunt_id else [(None,)]
        kwargs = [dict(since=since, tag=tag, rule_name=rule_name)]*len(args)
        for result in utils.parallel_executor_iterable_results(self.live_results, args_list=args, kwargs_list=kwargs):
            yield result

    def historical_delete_multiple(self, hunt_id):
        """
        Delete the historical hunt associated with the given hunt_id.

        :param hunt_id: List of hunt ids.
        :return: An iterator of hunt objects.
        """
        kwargs = [dict(hunt=h) for h in hunt_id]
        for result in utils.parallel_executor(self.historical_delete, kwargs_list=kwargs):
            yield result

    def historical_results_multiple(self, hunt_id, tag=None, rule_name=None):
        """
        Get results from historical hunt.

        :param hunt_id: List of hunt ids.
        :param tag: Filter results on this tag.
        :param rule_name: Filter results on this rule name.
        :return: An iterator of hunt objects.
        """
        args = [(h,) for h in hunt_id] if hunt_id else [(None,)]
        kwargs = [dict(tag=tag, rule_name=rule_name)] * len(args)
        for result in utils.parallel_executor_iterable_results(self.historical_results, args_list=args, kwargs_list=kwargs):
            yield result

    def tag_link_multiple(self, hashes, tags=None, families=None, emerging=None, remove=False):
        """
        Update a TagLink with the given type or value by its id.

        :param hashes: A list of sha256 of the artifacts.
        :param tags: A list of tags to be added or removed.
        :param families: A list of families to be added or removed.
        :param emerging: A boolean indicating if the artifacts should be flagged as emerging.
        :param remove: A flag indicating if we should remove the provided tags/families.
        :return: A TagLink resource
        """
        args = [(h,) for h in hashes]
        kwargs = [dict(tags=tags, families=families, emerging=emerging, remove=remove)] * len(args)
        for tag_link in utils.parallel_executor(
                self.tag_link_update,
                args_list=args,
                kwargs_list=kwargs,
        ):
            yield tag_link
