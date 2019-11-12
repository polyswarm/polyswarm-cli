import click
from .utils import validate_hashes, validate_hash
from polyswarm_api.types.resources import Hash


@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hash', nargs=-1, callback=validate_hashes)
@click.argument('destination', nargs=1, type=click.Path(file_okay=False))
@click.command('download', short_help='download file(s)')
@click.pass_context
def download(ctx, hash_file, hash_type, hash, destination):
    """
    Download files from matching hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    hashes = Hash.from_strings(hash, hash_type, hash_file)
    if not hashes:
        raise click.BadParameter('Hash not valid, must be sha256|md5|sha1 in hexadecimal format')

    for result in api.download(destination, *hashes):
        output.local_artifact(result)


@click.option('-s', '--since', type=click.IntRange(1, 2880), default=1440,
              help='Request archives X minutes into the past. Default: 1440, Max: 2880')
@click.argument('destination', nargs=1, type=click.Path(file_okay=False))
@click.command('stream', short_help='access the polyswarm file stream')
@click.pass_context
def stream(ctx, since, destination):
    api = ctx.obj['api']
    out = ctx.obj['output']

    for download in api.stream(destination, since=since):
        out.local_artifact(download)


@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hash', nargs=1, callback=validate_hash)
@click.command('cat', short_help='cat artifact to stdout')
@click.pass_context
def cat(ctx, hash_type, hash):
    api = ctx.obj['api']
    out = click.get_binary_stream('stdout')
    api.download_to_filehandle(hash, out)
