import logging
import os

from polyswarm.client import utils

import click

logger = logging.getLogger(__name__)


@click.command('download', short_help='Download file(s).')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5].', default=None)
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded files.', default=os.getcwd())
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes)
@click.pass_context
@utils.any_provided('hash_file', 'hash_value')
def download(ctx, hash_file, hash_type, destination, hash_value):
    """
    Download files from matching hashes
    """
    api = ctx.obj['api']
    out = ctx.obj['output']
    hashes = utils.parse_hashes(hash_value, hash_file=hash_file)
    for result in api.download_multiple(hashes, destination, hash_type):
        out.local_artifact(result)


@click.command('download-id', short_help='Download file(s).')
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded files.', default=os.getcwd())
@click.argument('instance_id', nargs=-1, type=click.INT)
@click.pass_context
def download_id(ctx, destination, instance_id):
    """
    Download files from instance ids
    """
    api = ctx.obj['api']
    out = ctx.obj['output']
    for result in api.download_id_multiple(instance_id, destination):
        out.local_artifact(result)


@click.command('download-sandbox-artifact', short_help='Download sandbox artifact file.')
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded files.', default=os.getcwd())
@click.argument('sandbox_task_id', type=click.INT)
@click.argument('instance_id', nargs=-1, type=click.INT)
@click.pass_context
def download_sandbox_artifact(ctx, destination, sandbox_task_id, instance_id):
    """
    Download files from instance ids
    """
    api = ctx.obj['api']
    out = ctx.obj['output']

    out.local_artifact(api.download_sandbox_artifact(destination, sandbox_task_id, instance_id))


@click.command('stream', short_help='Access the polyswarm file stream.')
@click.option('-s', '--since', type=click.IntRange(1, 2880), default=1440,
              help='Request archives X minutes into the past. Default: 1440, Max: 2880.')
@click.argument('destination', nargs=1, type=click.Path(file_okay=False))
@click.pass_context
def stream(ctx, since, destination):
    api = ctx.obj['api']
    out = ctx.obj['output']

    for result in api.download_stream(destination, since):
        out.local_artifact(result)


@click.command('cat', short_help='Output artifact contents to stdout.')
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5].', default=None)
@click.argument('hash_value', nargs=-1, callback=utils.validate_hashes, required=True)
@click.pass_context
def cat(ctx, hash_type, hash_value):
    api = ctx.obj['api']
    out = click.get_binary_stream('stdout')
    for h in hash_value:
        api.download_to_handle(h, out, hash_type=hash_type)
