import logging

import click

from . import utils

logger = logging.getLogger(__name__)


@click.command('download', short_help='download file(s)')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes)
@click.argument('destination', nargs=1, type=click.Path(file_okay=False))
@click.pass_context
def download(ctx, hash_file, hash_type, hash_value, destination):
    """
    Download files from matching hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    hashes = utils.parse_hashes(hash_value, hash_file=hash_file, hash_type=hash_type, log_errors=True)
    for result in api.download(destination, *hashes):
        output.local_artifact(result)


@click.command('stream', short_help='access the polyswarm file stream')
@click.option('-s', '--since', type=click.IntRange(1, 2880), default=1440,
              help='Request archives X minutes into the past. Default: 1440, Max: 2880')
@click.argument('destination', nargs=1, type=click.Path(file_okay=False))
@click.pass_context
def stream(ctx, since, destination):
    api = ctx.obj['api']
    out = ctx.obj['output']

    for download in api.stream(destination, since=since):
        out.local_artifact(download)


@click.command('cat', short_help='cat artifact to stdout')
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hash_value', callback=utils.validate_hash)
@click.pass_context
def cat(ctx, hash_type, hash_value):
    api = ctx.obj['api']
    out = click.get_binary_stream('stdout')
    hashes = utils.parse_hashes([hash_value], hash_type=hash_type, log_errors=True)
    api.download_to_filehandle(hashes[0], out)
