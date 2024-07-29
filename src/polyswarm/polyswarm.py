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
        super().__init__(*args, **kwargs)
        self.parallel = parallel

    def scan_file(self, path, recursive=False,
                  timeout=settings.DEFAULT_SCAN_TIMEOUT, nowait=False, scan_config=None,
                  preprocessing=None):
        """
        Scan files or directories via PolySwarm.

        :param path: A list of paths for files or directories.
        :param recursive: Scan directories recursively.
        :param timeout: How long to wait for results.
        :param nowait: Does not wait for the scan window to close, just create it and return right away.
        :param scan_config: Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".
        :param preprocessing: Preprocessing settings to be applied to the artifact, None means no preprocessing,
                              otherwise a dict with the following attributes can be passed:
                              - type (string): either "zip" or "qrcode", the first mean the file is a zip that
                                the server has to decompress to then scan the content (only one file inside allowed).
                                "qrcode" means the file is a QR Code image with a URL as payload, and you want
                                to scan the URL, not the actual file (artifact_type has to be "URL").
                              - password (string, optional): will use this password to decompress the zip file.
        :return: An iterator of artifact instances.
        """
        args = [(self, timeout, nowait, file) for file in utils.collect_files(path, recursive=recursive)]
        for instance in utils.parallel_executor(submit_and_wait,
                                                args_list=args,
                                                kwargs_list=[{
                                                    'scan_config': scan_config,
                                                    'preprocessing': preprocessing,
                                                }]*len(args)):
            yield instance

    def scan_url(self,
                 urls,
                 timeout=settings.DEFAULT_SCAN_TIMEOUT,
                 nowait=False,
                 scan_config='more-time',
                 preprocessing=None):
        """
        Scan files or directories via PolySwarm

        :param urls: A list of urls.
        :param timeout: How long to wait for results.
        :param nowait: Does not wait for the scan window to close, just create it and return right away.
        :param scan_config: Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".
        :param preprocessing: Preprocessing settings to be applied to the artifact, None means no preprocessing,
                              otherwise a dict with the following attributes can be passed:
                              - type (string): either "zip" or "qrcode", the first mean the file is a zip that
                                the server has to decompress to then scan the content (only one file inside allowed).
                                "qrcode" means the file is a QR Code image with a URL as payload, and you want
                                to scan the URL, not the actual file (artifact_type has to be "URL").
                              - password (string, optional): will use this password to decompress the zip file.
        :return: An iterator of artifact instances.
        """
        args = [(self, timeout, nowait, url) for url in urls]
        kwargs = [dict(artifact_type='url', scan_config=scan_config, preprocessing=preprocessing) for _ in urls]

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

    def download_id_multiple(self, instance_id, destination):
        """
        Download files from matching instance ids.

        :param instance_id: A list of instance ids to download.
        :param destination: Folder where to download the files to.
        :return: An iterator of local artifacts.
        """
        args = [(destination, h) for h in instance_id]

        for result in utils.parallel_executor(self.download_id, args_list=args):
            yield result

    def download_stream(self, destination, since=1440):
        """
        Access the polyswarm file stream.

        :param destination: Folder where to download the files to.
        :param since: Request archives X minutes into the past. Default: 1440, Max: 2880.
        :return: An iterator of local artifacts.
        """
        args = iter((destination, artifact_archive.uri) for artifact_archive in self.stream(since=since))
        for result in utils.parallel_executor(self.download_archive, args_list=args, max_workers=self.parallel):
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

    def historical_results_multiple(self, hunt_id, **kwargs):
        """
        Get results from historical hunt.

        :param hunt_id: List of hunt ids.
        :return: An iterator of hunt objects.
        """
        args = [(h,) for h in hunt_id] if hunt_id else [(None,)]
        kwargs = [kwargs] * len(args)
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

    def sandbox_instances(self, instance_ids, **kwargs):
        """
        Send a file to be sandboxed by instance id.
        """
        args = [(u,) for u in instance_ids]
        kwargs = [kwargs] * len(args)
        for result in utils.parallel_executor(self.sandbox, args_list=args, kwargs_list=kwargs):
            yield result
