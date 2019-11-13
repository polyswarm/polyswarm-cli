import logging
from uuid import UUID

import click
from polyswarm_api import exceptions
from polyswarm_api.types import resources

logger = logging.getLogger(__name__)


HASH_VALIDATORS = resources.Hash.SUPPORTED_HASH_TYPES


def is_valid_uuid(value):
    try:
        val = UUID(value, version=4)
        return True
    except:
        return False


def parse_hashes(values, hash_file=None, hash_type=None, log_errors=False):
    hashes = []
    if hash_file is not None:
        values += hash_file.read_lines()
    for hash_ in values:
        try:
            hashes.append(resources.Hash(hash_, hash_type=hash_type))
        except exceptions.InvalidValueException as e:
            if log_errors:
                logger.error(e)
            else:
                raise e
    if not hashes:
        raise click.BadParameter('Hash not valid, must be sha256|md5|sha1 in hexadecimal format')
    return hashes


####################################################
# Click parameters validators
####################################################


def validate_uuid(ctx, param, value):
    for uuid in value:
        if not is_valid_uuid(uuid):
            raise click.BadParameter('UUID {} not valid, please check and try again.'.format(uuid))
    return value


def validate_hash(ctx, param, h):
    hash_type = ctx.params.get('hash_type')
    if hash_type:
        validator = HASH_VALIDATORS.get(hash_type)
        if validator and validator(h):
            return h
    elif any(validator(h) for validator in HASH_VALIDATORS.values()):
        return h

    raise click.BadParameter('Hash {} not valid, must be sha256|md5|sha1 in hexadecimal format'.format(h))


def validate_hashes(ctx, param, value):
    for h in value:
        validate_hash(ctx, param, h)
    return value


def validate_key(ctx, param, value):
    if not resources.is_hex(value) or len(value) != 32:
        raise click.BadParameter('Invalid API key. Make sure you specified your key via -a or environment variable and try again.')
    return value
