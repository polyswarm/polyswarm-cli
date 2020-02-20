import logging
import os
from concurrent.futures import ThreadPoolExecutor
# TODO: Change this to import itertools once we drop support for python 2.7
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

import click
from polyswarm_api import exceptions as api_exceptions
from polyswarm_api.types import resources

from polyswarm import exceptions

logger = logging.getLogger(__name__)


HASH_VALIDATORS = resources.Hash.SUPPORTED_HASH_TYPES


def is_valid_id(value):
    try:
        int(value)
        return True
    except:
        return False


####################################################
# Parallelization and error handling executors
####################################################


def parallelize(function, args_list=(), kwargs_list=(), **kwargs):
    futures = []
    with ThreadPoolExecutor(**kwargs) as pool:
        for args, kwargs in zip_longest(args_list, kwargs_list, fillvalue=None):
            args = args or []
            kwargs = kwargs or {}
            futures.append(pool.submit(function, *args, **kwargs))
    for future in futures:
        yield future


def parallel_executor(function, args_list=(), kwargs_list=(), **kwargs):
    hard_failure = False
    soft_failure = False
    empty_results = False
    no_results = True
    for i, future in enumerate(parallelize(function, args_list=args_list, kwargs_list=kwargs_list, **kwargs)):
        try:
            yield future.result()
            no_results = False
        except api_exceptions.NoResultsException:
            logger.error('Polyswarm API call to {}({}) did not return any results'
                         .format(function.__name__, ', '.join(str(arg) for arg in args_list[i])))
            empty_results = True
        except api_exceptions.NotFoundException as e:
            logger.error(e)
            soft_failure = True
        except api_exceptions.PolyswarmException as e:
            logger.error(e)
            hard_failure = True

    if hard_failure:
        raise exceptions.InternalFailureException('One or more requests encountered unrecoverable errors. '
                                                  'Please check the logs.')
    if soft_failure:
        raise exceptions.NotFoundException('One or more requests did not find the requested resources. '
                                           'Please check the logs.')
    if no_results:
        raise exceptions.NoResultsException('No results returned. Please check the logs.')
    if empty_results:
        raise exceptions.NotFoundException('One or more items did not return any results. '
                                           'Please check the logs.')


def parallel_executor_iterable_results(search_method, args_list=(), kwargs_list=(), **kwargs):
    for results in parallel_executor(search_method, args_list=args_list, kwargs_list=kwargs_list, **kwargs):
        for result in results:
            yield result


####################################################
# Input parsers
####################################################

def _yield_files(base_path, files):
    for file in files:
        path = os.path.join(base_path, file)
        if os.path.isfile(path):
            yield path


def collect_files(paths, recursive=False, log_errors=False):
    all_files = []
    for path in paths:
        if os.path.isfile(path):
            all_files.append(path)
        elif os.path.isdir(path):
            if recursive:
                for sub_path, _, files in os.walk(path):
                    all_files.extend(_yield_files(sub_path, files))
            else:
                all_files.extend(_yield_files(path, os.listdir(path)))
        elif log_errors:
            logger.error('Path %s is neither a file nor a directory.', path)
        else:
            raise api_exceptions.InvalidValueException('Path {} is neither a file nor a directory.'.format(path))
    return all_files


def parse_hashes(values, hash_file=None):
    hashes = list(values)
    if hash_file is not None:
        hashes += hash_file.readlines()
    return hashes


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
    if not resources.is_hex(value) or len(value) != 32:
        raise click.BadParameter('Invalid API key. Make sure you specified your key via -a or environment variable and try again.')
    return value
