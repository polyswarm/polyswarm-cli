from __future__ import absolute_import
import click

from polyswarm.client import utils


@click.group(short_help='Interact with Tag links in Polyswarm.')
def link():
    pass


@link.command('set', short_help='Link and unlink tags/families with an artifact.')
@click.argument('sha256', type=click.STRING, required=True)
@click.option('-t', '--tag', type=click.STRING, multiple=True)
@click.option('-f', '--family', type=click.STRING, multiple=True)
@click.option('-r', '--remove', type=click.BOOL, is_flag=True)
@click.pass_context
@utils.any_provided('tag', 'family')
def update(ctx, sha256, tag, family, remove):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag_link(api.tag_link_update(
        sha256,
        tags=tag,
        families=family,
        remove=remove,
    ))


@link.command('view', short_help='View the tags/families linked with an artifact.')
@click.argument('sha256', type=click.STRING, required=True)
@click.pass_context
def view(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag_link(api.tag_link_get(sha256))


@link.command('list', short_help='List all links with the given tags/families.')
@click.option('-t', '--tag', type=click.STRING, multiple=True,
              help='A tag that must be associated with the artifact.')
@click.option('-f', '--family', type=click.STRING, multiple=True,
              help='A family that must be associated with the artifact.')
@click.option('-g', '--or-tag', type=click.STRING, multiple=True,
              help='At least one of the provided or-tags must be associated with the artifact.')
@click.option('-y', '--or-family', type=click.STRING, multiple=True,
              help='At least one of the provided or-families must be associated with the artifact.')
@click.pass_context
@utils.any_provided('tag', 'family', 'or_tag', 'or_family')
def list_links(ctx, tag, family, or_tag, or_family):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for tag_ in api.tag_link_list(tag, family, or_tag, or_family):
        output.tag_link(tag_)
