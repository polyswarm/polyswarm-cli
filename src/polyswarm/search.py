import sys
import json

import click
from polyswarm_api.log import logger
from polyswarm_api import exceptions
from polyswarm_api.types.query import MetadataQuery
from polyswarm_api.utils import parse_hashes


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
            all_failed = True
            for result in results:
                output.search_result(result)
                if not result.failed:
                    all_failed = False

            if all_failed:
                sys.exit(1)
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
        all_failed = True
        for result in api.search_by_metadata(*queries, with_instances=not without_bounties,
                                             with_metadata=not without_metadata):
            output.search_result(result)
            if not result.failed:
                all_failed = False

    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)

    if all_failed:
        sys.exit(1)
