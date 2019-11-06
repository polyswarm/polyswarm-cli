import os
import sys

import click
from polyswarm_api import exceptions
from .utils import validate_hashes, validate_hash
from polyswarm_api.utils import parse_hashes


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

    hashes = parse_hashes(hash, hash_type, hash_file)

    if hashes:
        try:
            any_failed = False
            for result in api.download(destination, *hashes):
                output.download_result(result)
                any_failed = result.failed or any_failed

            if any_failed:
                sys.exit(1)
        except exceptions.UsageLimitsExceeded:
            output.usage_exceeded()
            sys.exit(2)
    else:
        raise click.BadParameter('Hash not valid, must be sha256|md5|sha1 in hexadecimal format')


@click.option('-s', '--since', type=click.IntRange(1, 2880), default=1440,
              help='Request archives X minutes into the past. Default: 1440, Max: 2880')
@click.argument('destination', nargs=1, type=click.Path(file_okay=False))
@click.command('stream', short_help='access the polyswarm file stream')
@click.pass_context
def stream(ctx, since, destination):
    api = ctx.obj['api']
    out = ctx.obj['output']

    if destination is not None:
        if not os.path.exists(destination):
            os.makedirs(destination)

    try:
        any_failed = False
        for download in api.stream(destination, since=since):
            out.download_result(download)
            any_failed = download.failed or any_failed

        if any_failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        out.usage_exceeded()
        sys.exit(2)


@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hash', nargs=1, callback=validate_hash)
@click.command('cat', short_help='cat artifact to stdout')
@click.pass_context
def cat(ctx, hash_type, hash):
    api = ctx.obj['api']
    output = ctx.obj['output']
    # handle 2.7
    out = sys.stdout
    if hasattr(sys.stdout, 'buffer'):
        out = sys.stdout.buffer
    try:
        result = api.download_to_filehandle(hash, out)
        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)
