import logging
import json
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import click
from polyswarm_api.types import resources

from . import utils


logger = logging.getLogger(__name__)


@click.group(short_help='interact with PolySwarm search api')
def search():
    pass


@search.command('hash', short_help='search for hashes separated by space')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5]', default=None)
@click.argument('hash_value', nargs=-1)
@click.pass_context
def hashes(ctx, hash_value, hash_file, hash_type):
    """
    Search PolySwarm for files matching hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    hashes_ = utils.parse_hashes(hash_value, hash_file=hash_file, hash_type=hash_type, log_errors=True)

    results = api.search(*hashes_)

    # for json, this is effectively jsonlines
    for result in results:
        output.artifact_instance(result)


@search.command('metadata', short_help='search metadata of files')
@click.option('-r', '--query-file', help='Properly formatted JSON search file', type=click.File('r'))
@click.argument('query_string', nargs=-1)
@click.pass_context
def metadata(ctx, query_string, query_file):

    api = ctx.obj['api']
    output = ctx.obj['output']

    try:
        if len(query_string) >= 1:
            queries = [resources.MetadataQuery(q, False, api) for q in query_string]
        elif query_file:
            # TODO: support multiple queries in a file?
            queries = [resources.MetadataQuery(json.load(query_file), True, api)]
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
