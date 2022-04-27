from __future__ import absolute_import
import logging

from polyswarm.client import utils

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import click


logger = logging.getLogger(__name__)


@click.group(short_help='Interact search api.')
def search():
    pass


@search.command('hash', short_help='Search for hashes separated by space.')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('--hash-type', help='Hash type to search [default:autodetect, sha256|sha1|md5].', default=None)
@click.argument('hash_value', nargs=-1)
@click.pass_context
@utils.any_provided('hash_value', 'hash_file')
def hashes(ctx, hash_value, hash_file, hash_type):
    """
    Search PolySwarm for files matching hashes
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    hashes = utils.parse_hashes(hash_value, hash_file=hash_file)
    for instance in api.search_hashes(hashes, hash_type):
        output.artifact_instance(instance)


@search.command('url', short_help='Search for urls separated by space.')
@click.argument('url', nargs=-1, required=True)
@click.pass_context
def urls(ctx, url):
    """
    Search PolySwarm for a scan matching the url
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for instance in api.search_urls(url):
        output.artifact_instance(instance)


@search.command('metadata', short_help='Search metadata of files.')
@click.option('-i', '--include', type=click.STRING, multiple=True,
              help='Field to be included in the result (.* wildcards are accepted).')
@click.option('-x', '--exclude', type=click.STRING, multiple=True,
              help='Field to be excluded from the result (.* wildcards are accepted).')
@click.option('-p', '--ip', type=click.STRING, multiple=True,
              help='IP address IOC to search')
@click.option('-u', '--url', type=click.STRING, multiple=True,
              help='URL address IOC to search')
@click.option('-d', '--domain', type=click.STRING, multiple=True,
              help='Domain address IOC to search')
@click.argument('query_string', nargs=-1, required=False)
@click.pass_context
def metadata(ctx, query_string, include, exclude, ip, url, domain):
    api = ctx.obj['api']
    output = ctx.obj['output']
    query_string = ' '.join(query_string)

    if sum([not ip, not url, not domain]) < 2:
        raise click.exceptions.BadParameter("Only one of the following paramters may be provided per request: ip, url, or domain")

    for metadata_result in api.search_by_metadata(query_string, include=include, exclude=exclude, ips=ip, urls=url, domains=domain):
        output.metadata(metadata_result)


@search.command('mapping', short_help='Retrieve the metadata search mapping.')
@click.pass_context
def mapping(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.mapping(api.metadata_mapping())


@search.command('scans', short_help='Search for all scans or a particular artifact.')
@click.argument('hash_value', required=True)
@click.pass_context
def scans(ctx, hash_value):
    """
    Search PolySwarm for scans of a particular artifact
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    for instance in api.search_scans(hash_value):
        output.artifact_instance(instance)

