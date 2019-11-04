import os
import sys
import json

import click
from polyswarm_api.log import logger
from polyswarm_api import exceptions
from polyswarm_api.types.query import MetadataQuery
from polyswarm_api.utils import parse_hashes
from polyswarm_api.analyzers import DEFAULT_FEATURES


@click.group(short_help='interact with PolySwarm search api')
def search():
    pass


@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.option('-m', '--without-metadata', is_flag=True, default=False,
              help='Don\'t request artifact metadata.')
@click.option('-b', '--without-bounties', is_flag=True, default=False,
              help='Don\'t request bounties.')
@click.argument('hashes', nargs=-1)
@search.command('hash', short_help='search for hashes separated by space')
@click.pass_context
def hashes(ctx, hashes, hash_file, hash_type, without_metadata, without_bounties):
    """
    Search PolySwarm for files matching hashes
    """

    api = ctx.obj['api']
    output = ctx.obj['output']

    hashes = parse_hashes(hashes, hash_type, hash_file)
    try:
        if hashes:
            results = api.search(*hashes, with_instances=not without_bounties, with_metadata=not without_metadata)

            # for json, this is effectively jsonlines
            for result in results:
                output.search_result(result)
        else:
            raise click.BadParameter('Hash not valid, must be sha256|md5|sha1 in hexadecimal format')
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(1)


@click.option('-r', '--query-file', help='Properly formatted JSON search file', type=click.File('r'))
@click.option('-m', '--without-metadata', is_flag=True, default=False,
              help='Don\'t request artifact metadata.')
@click.option('-b', '--without-bounties', is_flag=True, default=False,
              help='Don\'t request bounties.')
@click.argument('query_string', nargs=-1)
@search.command('metadata', short_help='search metadata of files')
@click.pass_context
def metadata(ctx, query_string, query_file, without_metadata, without_bounties):

    api = ctx.obj['api']
    output = ctx.obj['output']

    try:
        if len(query_string) >= 1:
            queries = [MetadataQuery(q, False, api) for q in query_string]
        elif query_file:
            # TODO support multiple queries in a file?
            queries = [MetadataQuery(json.load(query_file), True, api)]
        else:
            logger.error('No query specified')
            return 0
    except json.decoder.JSONDecodeError:
        logger.error('Failed to parse JSON')
        return 0
    except UnicodeDecodeError:
        logger.error('Failed to parse JSON due to Unicode error')
        return 0

    try:
        for result in api.search_by_metadata(*queries, with_instances=not without_bounties,
                                             with_metadata=not without_metadata):
            output.search_result(result)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(1)


@click.option('-r', '--recursive', is_flag=True, default=False, help='Scan directories recursively')
@click.option('-f', '--features', type=click.STRING, help='Comma seperated list of features to search (i.e. strings.domains,pefile.imphash)')
@click.argument('path', nargs=-1, type=click.Path(exists=True))
@search.command('features', short_help='search features of files')
@click.pass_context
def features(ctx, path, recursive, features):

    api = ctx.obj['api']
    output = ctx.obj['output']

    features = features.split(',') if features else DEFAULT_FEATURES

    paths = path

    files = []
    for path in paths:
        if os.path.isfile(path):
            files.append(path)
        elif os.path.isdir(path):
            if recursive:
                files.extend([os.path.join(path, file)
                             for (path, dirs, fs) in os.walk(path)
                             for file in fs if os.path.isfile(os.path.join(path, file))])
            else:
                files.extend([os.path.join(path, file) for file in os.listdir(path)
                             if os.path.isfile(os.path.join(path, file))])
        else:
            logger.warning('Path %s is neither a file nor a directory, ignoring.', path)

    try:
        for result in api.search_by_feature(features, *files):
            output.search_result(result)

    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(1)
