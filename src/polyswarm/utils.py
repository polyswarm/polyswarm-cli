import click

from uuid import UUID
from polyswarm_api.types.hash import is_valid_sha256, is_valid_sha1, is_valid_md5, is_hex


def is_valid_uuid(value):
    try:
        val = UUID(value, version=4)
        return True
    except:
        return False


def validate_uuid(ctx, param, value):
    for uuid in value:
        if not is_valid_uuid(uuid):
            raise click.BadParameter('UUID {} not valid, please check and try again.'.format(uuid))
    return value


def validate_hash(ctx, param, h):
    if not (is_valid_sha256(h) or is_valid_md5(h) or is_valid_sha1(h)):
        raise click.BadParameter('Hash {} not valid, must be sha256|md5|sha1 in hexadecimal format'.format(h))
    return h


def validate_hashes(ctx, param, value):
    for h in value:
        validate_hash(ctx, param, h)
    return value


def validate_key(ctx, param, value):
    if not is_hex(value) or len(value) != 32:
        raise click.BadParameter('Invalid API key. Make sure you specified your key via -a or environment variable and try again.')
    return value
