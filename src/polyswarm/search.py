import logging
import json

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import click
from polyswarm_api.types import resources

from polyswarm import utils


logger = logging.getLogger(__name__)


@click.group(short_help='Interact with PolySwarm search api')
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
    args = [(h,) for h in utils.parse_hashes(hash_value, hash_file=hash_file)]
    for instance in utils.parallel_executor_iterable_results(api.search, args_list=args,
                                                             kwargs_list=[{'hash_type': hash_type}]*len(args)):
        output.artifact_instance(instance)


@search.command('metadata', short_help='search metadata of files')
@click.option('-r', '--query-file', help='Properly formatted JSON search file', type=click.File('r'))
@click.argument('query_string', nargs=-1)
@click.pass_context
def metadata(ctx, query_string, query_file):

    api = ctx.obj['api']
    output = ctx.obj['output']
    queries = [resources.MetadataQuery(q, False, api) for q in query_string]
    if query_file:
        queries.append(resources.MetadataQuery(json.load(query_file), True, api))
    args = [(q,) for q in queries]
    for instance in utils.parallel_executor_iterable_results(api.search_by_metadata, args_list=args):
        output.artifact_instance(instance)
