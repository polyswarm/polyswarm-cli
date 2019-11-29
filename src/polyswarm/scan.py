import logging

import click

from polyswarm_api import const
from polyswarm_api import exceptions
from . import utils

logger = logging.getLogger(__name__)


@click.command('scan', short_help='scan files/directories')
@click.option('-r', '--recursive', is_flag=True, default=False, help='Scan directories recursively')
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {})'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.argument('path', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def scan(ctx, recursive, timeout, path):
    """
    Scan files or directories via PolySwarm
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    args = [(file,) for file in utils.collect_files(path, recursive=recursive)]

    for future in utils.parallelize(api.submit, args_list=args):
        instance = future.result()
        try:
            output.artifact_instance(api.wait_for(instance.id, timeout=timeout))
        except exceptions.TimeoutException:
            output.artifact_instance(next(api.lookup(instance.id)))


@click.command('url', short_help='scan url')
@click.option('-r', '--url-file', help='File of URLs, one per line.', type=click.File('r'))
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {})'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.argument('url', nargs=-1, type=click.STRING)
@click.pass_context
def url_scan(ctx, url_file, timeout, url):
    """
    Scan files or directories via PolySwarm
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    urls = list(url)
    if url_file:
        urls.extend([u.strip() for u in url_file.readlines()])
    args = [(url,) for url in urls]
    kwargs = [dict(artifact_type='url') for _ in urls]

    for future in utils.parallelize(api.submit, args_list=args, kwargs_list=kwargs):
        instance = future.result()
        try:
            output.artifact_instance(api.wait_for(instance.id, timeout=timeout))
        except exceptions.TimeoutException:
            output.artifact_instance(next(api.lookup(instance.id)))


@click.command('rescan', short_help='rescan files(s) by hash')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {})'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes)
@click.pass_context
def rescan(ctx, hash_file, hash_type, timeout, hash_value):
    """
    Rescan files with matched hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    args = [(h,) for h in utils.parse_hashes(hash_value, hash_file=hash_file, hash_type=hash_type, log_errors=True)]

    for future in utils.parallelize(api.rescan, args_list=args):
        instance = future.result()
        try:
            output.artifact_instance(api.wait_for(instance.id, timeout=timeout))
        except exceptions.TimeoutException:
            output.artifact_instance(next(api.lookup(instance.id)))


@click.command('lookup', short_help='lookup Submission id(s)')
@click.option('-r', '--submission-id-file', help='File of Submission ids, one per line.', type=click.File('r'))
@click.argument('submission_id', nargs=-1, callback=utils.validate_id)
@click.pass_context
def lookup(ctx, submission_id, submission_id_file):
    """
    Lookup a PolySwarm scan by Submission id for current status.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    submission_ids = list(submission_id)

    # TODO dedupe
    if submission_id_file:
        for u in submission_id_file.readlines():
            u = u.strip()
            if utils.is_valid_id(u):
                submission_ids.append(u)
            else:
                logger.warning('Invalid Submission id %s in file, ignoring.', u)

    for future in utils.parallelize(api.lookup, args_list=[(u,) for u in submission_ids]):
        output.artifact_instance(future.result())
