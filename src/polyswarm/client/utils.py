from __future__ import absolute_import
import logging
import functools

import click

from polyswarm import exceptions
from polyswarm.utils import is_valid_id
from polyswarm_api import resources

logger = logging.getLogger(__name__)
HASH_VALIDATORS = resources.Hash.SUPPORTED_HASH_TYPES

####################################################
# Input parsers
####################################################


def parse_hashes(hashes, hash_file=None):
    hashes = list(hashes)
    if hash_file is not None:
        hashes += hash_file.readlines()

    return [h.strip('\n') for h in hashes]


####################################################
# Click parameters validators
####################################################


def validate_id(ctx, param, value):
    for id_ in value:
        if not is_valid_id(id_):
            raise click.BadParameter('Id {} not valid, please check and try again.'.format(id_))
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
    if not resources.core.is_hex(value) or len(value) != 32:
        raise click.BadParameter('Invalid API key. Make sure you specified your key via -a or environment variable and try again.')
    return value


def true_value_safe_bool(value):
    return True if isinstance(value, bool) else bool(value)


def any_provided(*required):
    if not required:
        raise exceptions.PolyswarmException('At least one required click argument must be provided.')

    def wrap(f):
        @functools.wraps(f)
        def any_validator(ctx, **kwargs):
            if not any(true_value_safe_bool(kwargs[r]) for r in required):
                required_commands = {c.name: c for c in ctx.command.params[::-1] if c.name in required}
                if len(required) > 1:
                    human_names = [c.human_readable_name for c in required_commands.values()]
                    names = "|".join(human_names)
                    raise click.exceptions.BadArgumentUsage('At least one of [{}] should be provided.'.format(names))
                else:
                    raise click.exceptions.MissingParameter(ctx=ctx, param=required_commands[required[0]])
            return f(ctx, **kwargs)

        return any_validator

    return wrap
