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

    files = utils.collect_files(path, recursive=recursive)

    for submission in api.submit(*files):
        try:
            output.submission(api.wait_for(submission.uuid, timeout=timeout))
        except exceptions.TimeoutException:
            output.submission(next(api.lookup(submission.uuid)))


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

    for submission in api.submit(*urls, artifact_type='url'):
        try:
            output.submission(api.wait_for(submission.uuid, timeout=timeout))
        except exceptions.TimeoutException:
            output.submission(next(api.lookup(submission.uuid)))


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
    hashes = utils.parse_hashes(hash_value, hash_file=hash_file, hash_type=hash_type, log_errors=True)

    for submission in api.rescan(*hashes):
        try:
            output.submission(api.wait_for(submission.uuid, timeout=timeout))
        except exceptions.TimeoutException:
            output.submission(next(api.lookup(submission.uuid)))


@click.command('lookup', short_help='lookup UUID(s)')
@click.option('-r', '--uuid-file', help='File of UUIDs, one per line.', type=click.File('r'))
@click.argument('uuid', nargs=-1, callback=utils.validate_uuid)
@click.pass_context
def lookup(ctx, uuid, uuid_file):
    """
    Lookup a PolySwarm scan by UUID for current status.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    uuids = list(uuid)

    # TODO dedupe
    if uuid_file:
        for u in uuid_file.readlines():
            u = u.strip()
            if utils.is_valid_uuid(u):
                uuids.append(u)
            else:
                logger.warning('Invalid uuid %s in file, ignoring.', u)

    for result in api.lookup(*uuids):
        output.submission(result)
