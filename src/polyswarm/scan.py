import logging

import click

from polyswarm_api import const
from . import utils

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


def rescanid_and_wait(api, timeout, nowait, *args, **kwargs):
    instance = api.rescanid(*args, **kwargs)
    if nowait:
        return instance
    return api.wait_for(instance.id, timeout=timeout)


@click.group(short_help='Interact with Submissions sent to Polyswarm')
def scan():
    pass


@scan.command('file', short_help='Scan files/directories')
@click.option('-r', '--recursive', is_flag=True, default=False, help='Scan directories recursively')
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {})'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the submission window to close, just create it and return right away.')
@click.argument('path', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def file(ctx, recursive, timeout, nowait, path):
    """
    Scan files or directories via PolySwarm
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    args = [(api, timeout, nowait, file) for file in utils.collect_files(path, recursive=recursive)]

    for instance in utils.parallel_executor(submit_and_wait, args_list=args):
        output.artifact_instance(instance)


@scan.command('url', short_help='Scan url')
@click.option('-r', '--url-file', help='File of URLs, one per line.', type=click.File('r'))
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {})'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the submission window to close, just create it and return right away.')
@click.argument('url', nargs=-1, type=click.STRING)
@click.pass_context
def url_(ctx, url_file, timeout, nowait, url):
    """
    Scan files or directories via PolySwarm
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    urls = list(url)
    if url_file:
        urls.extend([u.strip() for u in url_file.readlines()])
    args = [(api, timeout, nowait, url) for url in urls]
    kwargs = [dict(artifact_type='url') for _ in urls]

    for instance in utils.parallel_executor(submit_and_wait, args_list=args, kwargs_list=kwargs):
        output.artifact_instance(instance)


@click.command('rescan', short_help='Rescan files(s) by hash')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {})'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the submission window to close, just create it and return right away.')
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes)
@click.pass_context
def rescan(ctx, hash_file, hash_type, timeout, nowait, hash_value):
    """
    Rescan files with matched hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    args = [(api, timeout, nowait, h) for h in utils.parse_hashes(hash_value, hash_file=hash_file)]

    for instance in utils.parallel_executor(rescan_and_wait, args_list=args,
                                            kwargs_list=[{'hash_type': hash_type}]*len(args)):
        output.artifact_instance(instance)


@click.command('rescanid', short_help='Rescan by submission id')
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {})'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the submission window to close, just create it and return right away.')
@click.argument('submission_id', nargs=-1, callback=utils.validate_id)
@click.pass_context
def rescanid(ctx, timeout, nowait, submission_id):
    """
    Rescan based on the id of a previous scan
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    args = [(api, timeout, nowait, s) for s in submission_id]

    for instance in utils.parallel_executor(rescanid_and_wait, args_list=args):
        output.artifact_instance(instance)


@click.command('lookup', short_help='Lookup a Submission id(s)')
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

    for result in utils.parallel_executor(api.lookup, args_list=[(u,) for u in submission_ids]):
        output.artifact_instance(result)


@click.command('wait', short_help='Wait for a  Submission to finish')
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {})'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.argument('submission_id', nargs=-1, callback=utils.validate_id)
@click.pass_context
def wait(ctx, submission_id, timeout):
    """
    Lookup a PolySwarm scan by Submission id for current status.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    args = [(s,) for s in submission_id]
    kwargs = [dict(timeout=timeout)]*len(args)

    for result in utils.parallel_executor(api.wait_for, args_list=args, kwargs_list=kwargs):
        output.artifact_instance(result)

