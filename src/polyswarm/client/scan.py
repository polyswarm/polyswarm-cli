import logging

import click

from polyswarm_api import const
from polyswarm import utils

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with Scans sent to Polyswarm.')
def scan():
    pass


@scan.command('file', short_help='Scan files/directories.')
@click.option('-r', '--recursive', is_flag=True, default=False, help='Scan directories recursively.')
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {}).'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the scan window to close, just create it and return right away.')
@click.option('-s', '--scan-config', type=click.STRING, default=None,
              help='Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".')
@click.argument('path', nargs=-1, type=click.Path(exists=True), required=True)
@click.pass_context
def file(ctx, recursive, timeout, nowait, path, scan_config):
    """
    Scan files or directories via PolySwarm
    """
    ps = ctx.obj['polyswarm']
    output = ctx.obj['output']

    for instance in ps.scan_file(recursive, timeout, nowait, path, scan_config):
        output.artifact_instance(instance)


@scan.command('url', short_help='Scan url.')
@click.option('-r', '--url-file', help='File of URLs, one per line.', type=click.File('r'))
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {}).'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the scan window to close, just create it and return right away.')
@click.option('-s', '--scan-config', type=click.STRING, default='more-time',
              help='Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".')
@click.argument('url', nargs=-1, type=click.STRING)
@click.pass_context
@utils.any_provided('url', 'url_file')
def url_(ctx, url_file, timeout, nowait, url, scan_config):
    """
    Scan files or directories via PolySwarm
    """
    ps = ctx.obj['polyswarm']
    output = ctx.obj['output']

    for instance in ps.scan_url(url_file, timeout, nowait, url, scan_config):
        output.artifact_instance(instance)


@click.command('rescan', short_help='Rescan files(s) by hash.')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5].', default=None)
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {}).'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the scan window to close, just create it and return right away.')
@click.option('-s', '--scan-config', type=click.STRING, default=None,
              help='Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".')
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes)
@click.pass_context
@utils.any_provided('hash_value', 'hash_file')
def rescan(ctx, hash_file, hash_type, timeout, nowait, hash_value, scan_config):
    """
    Rescan files with matched hashes
    """
    ps = ctx.obj['polyswarm']
    output = ctx.obj['output']

    for instance in ps.scan_rescan(hash_file, hash_type, timeout, nowait, hash_value, scan_config):
        output.artifact_instance(instance)


@click.command('rescan-id', short_help='Rescan by scan id.')
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {}).'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the scan window to close, just create it and return right away.')
@click.option('-s', '--scan-config', type=click.STRING, default=None,
              help='Configuration template to be used in the scan. E.g.: "default", "more-time", "most-time".')
@click.argument('scan_id', nargs=-1, callback=utils.validate_id, required=True)
@click.pass_context
def rescan_id(ctx, timeout, nowait, scan_id, scan_config):
    """
    Rescan based on the id of a previous scan
    """
    ps = ctx.obj['polyswarm']
    output = ctx.obj['output']

    for instance in ps.scan_rescan(timeout, nowait, scan_id, scan_config):
        output.artifact_instance(instance)


@click.command('lookup', short_help='Lookup a scan id(s).')
@click.option('-r', '--scan-id-file', help='File of scan ids, one per line.', type=click.File('r'))
@click.argument('scan_id', nargs=-1, callback=utils.validate_id)
@click.pass_context
@utils.any_provided('scan_id', 'scan_id_file')
def lookup(ctx, scan_id, scan_id_file):
    """
    Lookup a PolySwarm scan by Scan id for current status.
    """
    ps = ctx.obj['polyswarm']
    output = ctx.obj['output']

    for instance in ps.scan_lookup(scan_id, scan_id_file):
        output.artifact_instance(instance)


@click.command('wait', short_help='Wait for a  scan to finish.')
@click.option('-t', '--timeout', type=click.INT, default=const.DEFAULT_SCAN_TIMEOUT,
              help='How long to wait for results (default: {}).'.format(const.DEFAULT_SCAN_TIMEOUT))
@click.argument('scan_id', nargs=-1, callback=utils.validate_id, required=True)
@click.pass_context
def wait(ctx, scan_id, timeout):
    """
    Lookup a PolySwarm scan by Scan id for current status.
    """
    ps = ctx.obj['polyswarm']
    output = ctx.obj['output']

    for instance in ps.scan_lookup(scan_id, timeout):
        output.artifact_instance(instance)
