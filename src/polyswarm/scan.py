import logging
import os

import click
from polyswarm_api.types.resources import Hash

from . import utils

logger = logging.getLogger(__name__)


@click.command('scan', short_help='scan files/directories')
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force re-scan even if file has already been analyzed.')
@click.option('-r', '--recursive', is_flag=True, default=False, help='Scan directories recursively')
@click.argument('path', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def scan(ctx, path, force, recursive):
    """
    Scan files or directories via PolySwarm
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    paths = path

    directories, files = [], []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
        elif os.path.isdir(path):
            directories.append(path)
        else:
            logger.warning('Path %s is neither a file nor a directory, ignoring.', path)

    for result in api.scan(*files):
        output.submission(result)

    for d in directories:
        for result in api.scan_directory(d, recursive=recursive):
            output.submission(result)


@click.command('url', short_help='scan url')
@click.option('-r', '--url-file', help='File of URLs, one per line.', type=click.File('r'))
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force re-scan even if file has already been analyzed.')
@click.option('-t', '--timeout', type=click.INT, default=-1, help='How long to wait for results (default: forever, -1)')
@click.argument('url', nargs=-1, type=click.STRING)
@click.pass_context
def url_scan(ctx, url, url_file, force, timeout):
    """
    Scan files or directories via PolySwarm
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    api.timeout = timeout

    urls = list(url)

    if url_file:
        urls.extend([u.strip() for u in url_file.readlines()])

    for result in api.scan_urls(*urls):
        output.submission(result)


@click.command('rescan', short_help='rescan files(s) by hash')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes)
@click.pass_context
def rescan(ctx, hash_file, hash_type, hash_value):
    """
    Rescan files with matched hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    hashes = utils.parse_hashes(hash_value, hash_file=hash_file, hash_type=hash_type, log_errors=True)

    for result in api.rescan(*hashes):
        output.submission(result)


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
