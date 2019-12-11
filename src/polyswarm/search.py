import logging
import json

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import click
from polyswarm_api.types import resources

from polyswarm import utils
from polyswarm import exceptions


logger = logging.getLogger(__name__)


@click.group(short_help='Interact with PolySwarm search api')
def search():
    pass


def process_search(ctx, search_method, args_list=(), kwargs_list=()):
    output = ctx.obj['output']
    results_found = False
    partial_results = False
    for results in utils.parallel_executor(search_method, args_list=args_list, kwargs_list=kwargs_list):
        empty_result = True
        for result in results:
            results_found = True
            empty_result = False
            output.artifact_instance(result)
        partial_results = partial_results or empty_result

    if not results_found:
        raise exceptions.NoResultsException('One or more items did not return any results. '
                                            'Please check the logs.')
    if partial_results:
        raise exceptions.PartialResultsException('One or more items did not return any results. '
                                                 'Please check the logs.')


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
    args = [(h,) for h in utils.parse_hashes(hash_value, hash_file=hash_file, hash_type=hash_type, log_errors=True)]
    process_search(ctx, api.search, args_list=args)


@search.command('metadata', short_help='search metadata of files')
@click.option('-r', '--query-file', help='Properly formatted JSON search file', type=click.File('r'))
@click.argument('query_string', nargs=-1)
@click.pass_context
def metadata(ctx, query_string, query_file):

    api = ctx.obj['api']

    queries = [resources.MetadataQuery(q, False, api) for q in query_string]
    if query_file:
        queries.append(resources.MetadataQuery(json.load(query_file), True, api))
    args = [(q,) for q in queries]
    process_search(ctx, api.search_by_metadata, args_list=args)
