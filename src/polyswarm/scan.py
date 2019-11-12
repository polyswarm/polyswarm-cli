import logging
import os

import click
from polyswarm_api.types.resources import Hash

from .utils import validate_uuid, is_valid_uuid, validate_hashes

logger = logging.getLogger(__name__)


@click.option('-f', '--force', is_flag=True, default=False,
              help='Force re-scan even if file has already been analyzed.')
@click.option('-r', '--recursive', is_flag=True, default=False, help='Scan directories recursively')
@click.argument('path', nargs=-1, type=click.Path(exists=True))
@click.command('scan', short_help='scan files/directories')
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
        output.scan_result(result)

    for d in directories:
        for result in api.scan_directory(d, recursive=recursive):
            output.scan_result(result)


@click.option('-r', '--url-file', help='File of URLs, one per line.', type=click.File('r'))
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force re-scan even if file has already been analyzed.')
@click.option('-t', '--timeout', type=click.INT, default=-1, help='How long to wait for results (default: forever, -1)')
@click.argument('url', nargs=-1, type=click.STRING)
@click.command('url', short_help='scan url')
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
        output.scan_result(result)


@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hash', nargs=-1, callback=validate_hashes)
@click.command('rescan', short_help='rescan files(s) by hash')
@click.pass_context
def rescan(ctx, hash_file, hash_type, hash):
    """
    Rescan files with matched hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    hashes = Hash.from_strings(hash, hash_type, hash_file)
    if not hashes:
        raise click.BadParameter('Hash not valid, must be sha256|md5|sha1 in hexadecimal format')

    for result in api.rescan(*hashes):
        output.scan_result(result)


@click.option('-r', '--uuid-file', help='File of UUIDs, one per line.', type=click.File('r'))
@click.argument('uuid', nargs=-1, callback=validate_uuid)
@click.command('lookup', short_help='lookup UUID(s)')
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
            if is_valid_uuid(u):
                uuids.append(u)
            else:
                logger.warning('Invalid uuid %s in file, ignoring.', u)

    for result in api.lookup(*uuids):
        output.scan_result(result)
