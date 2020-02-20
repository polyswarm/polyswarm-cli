import logging

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import click

from . import utils

logger = logging.getLogger(__name__)


@click.command('download', short_help='Download file(s).')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5].', default=None)
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes)
@click.argument('destination', nargs=1, type=click.Path(file_okay=False))
@click.pass_context
def download(ctx, hash_file, hash_type, hash_value, destination):
    """
    Download files from matching hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    args = [(destination, h) for h in utils.parse_hashes(hash_value, hash_file=hash_file)]

    for result in utils.parallel_executor(api.download, args_list=args,
                                          kwargs_list=[{'hash_type': hash_type}]*len(args)):
        output.local_artifact(result)


@click.command('stream', short_help='Access the polyswarm file stream.')
@click.option('-s', '--since', type=click.IntRange(1, 2880), default=1440,
              help='Request archives X minutes into the past. Default: 1440, Max: 2880.')
@click.argument('destination', nargs=1, type=click.Path(file_okay=False))
@click.pass_context
def stream(ctx, since, destination):
    api = ctx.obj['api']
    out = ctx.obj['output']

    args = [(destination, artifact_archive.uri) for artifact_archive in api.stream(since=since)]
    for result in utils.parallel_executor(api.download_archive, args_list=args):
        out.local_artifact(result)


@click.command('cat', short_help='Output artifact contents to stdout.')
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5].', default=None)
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes)
@click.pass_context
def cat(ctx, hash_type, hash_value):
    api = ctx.obj['api']
    out = click.get_binary_stream('stdout')
    for h in hash_value:
        api.download_to_handle(h, out, hash_type=hash_type)
