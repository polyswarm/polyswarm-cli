import logging
import json

import click
from polyswarm_api.types.local import MetadataQuery
from polyswarm_api.types.base import parse_hashes

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

logger = logging.getLogger(__name__)


@click.group(short_help='interact with PolySwarm search api')
def search():
    pass


@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hashes', nargs=-1)
@search.command('hash', short_help='search for hashes separated by space')
@click.pass_context
def hashes(ctx, hashes, hash_file, hash_type):
    """
    Search PolySwarm for files matching hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    hashes = parse_hashes(hashes, hash_type, hash_file)
    if not hashes:
        raise click.BadParameter('Hash not valid, must be sha256|md5|sha1 in hexadecimal format')

    results = api.search(*hashes)

    # for json, this is effectively jsonlines
    for result in results:
        output.artifact_instance(result)


@click.option('-r', '--query-file', help='Properly formatted JSON search file', type=click.File('r'))
@click.argument('query_string', nargs=-1)
@search.command('metadata', short_help='search metadata of files')
@click.pass_context
def metadata(ctx, query_string, query_file):

    api = ctx.obj['api']
    output = ctx.obj['output']

    try:
        if len(query_string) >= 1:
            queries = [MetadataQuery(q, False, api) for q in query_string]
        elif query_file:
            # TODO: support multiple queries in a file?
            queries = [MetadataQuery(json.load(query_file), True, api)]
        else:
            logger.error('No query specified')
            return 0
    except JSONDecodeError:
        logger.error('Failed to parse JSON')
        return 0
    except UnicodeDecodeError:
        logger.error('Failed to parse JSON due to Unicode error')
        return 0

    for result in api.search_by_metadata(*queries):
        output.artifact_instance(result)
