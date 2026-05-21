import logging

from polyswarm.client import utils

import click


logger = logging.getLogger(__name__)


@click.group(short_help='Interact search api.')
def search():
    pass


@click.group(short_help='Interact with known ioc api.')
def known():
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
              help='URL IOC to search')
@click.option('-d', '--domain', type=click.STRING, multiple=True,
              help='Domain name IOC to search')
@click.argument('query_string', nargs=-1, required=False)
@click.pass_context
def metadata(ctx, query_string, include, exclude, ip, url, domain):
    api = ctx.obj['api']
    output = ctx.obj['output']
    query_string = ' '.join(query_string)

    for metadata_result in api.search_by_metadata(query_string, include=include, exclude=exclude, ips=ip, urls=url, domains=domain):
        output.metadata(metadata_result)


@search.command('ioc', short_help='Retrieve IOCs by artifact hash.')
@click.option('-h', '--hide-known-good', type=click.BOOL, is_flag=True)
@click.argument('type',  required=True,
                type=click.Choice(['ip', 'domain', 'ttp', 'imphash', 'sha256', 'sha1', 'md5'], case_sensitive=False))
@click.argument('value', required=True)
@click.pass_context
def iocs_by_hash(ctx, type, value, hide_known_good):
    """
    Provide an artifact hash to get the associated IOCs.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    params = dict()
    if type == 'ip':
        params['ip'] = value
    elif type == 'domain':
        params['domain'] = value
    elif type == 'ttp':
        params['ttp'] = value
    elif type == 'imphash':
        params['imphash'] = value

    if params:
        for result in api.search_by_ioc(**params):
            output.ioc(result)
    else:
        output.ioc(api.iocs_by_hash(type, value, hide_known_good=hide_known_good))


@search.command('known', short_help='Check if host is known.')
@click.option('-p', '--ip', type=click.STRING, multiple=True)
@click.option('-d', '--domain', type=click.STRING, multiple=True)
@click.pass_context
def search_known(ctx, ip, domain):
    """
    Check if an ip address or domain is known.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for result in api.check_known_hosts(ips=ip, domains=domain):
        output.known_host(result)


@known.command('add', short_help='Add a known host.')
@click.argument('type', required=True)
@click.argument('host', required=True)
@click.argument('source', required=True)
@click.pass_context
def add(ctx, type, host, source):
    """
    Add a known good ip or domain.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.known_host(api.add_known_good_host(type, source, host))


@known.command('update', short_help='Update a known host.')
@click.option('-g', '--good', type=click.BOOL)
@click.argument('id', required=True)
@click.argument('type', required=True)
@click.argument('host', required=True)
@click.argument('source', required=True)
@click.pass_context
def update(ctx, id, type, host, source, good):
    """
    Update a known ip address or domain.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.known_host(api.update_known_good_host(id, type, source, host, good))


@known.command('delete', short_help='Delete a known host.')
@click.argument('id', required=True)
@click.pass_context
def delete(ctx, id):
    """
    Delete a known ip address or domain.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.known_host(api.delete_known_good_host(id))


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
