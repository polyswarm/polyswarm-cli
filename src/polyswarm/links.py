import click


@click.group(short_help='Interact with Tag links in Polyswarm.')
def link():
    pass


@link.command('set', short_help='Link and unlink tags/families with an artifact.')
@click.argument('sha256', type=click.STRING)
@click.option('-t', '--tag', type=click.STRING, multiple=True)
@click.option('-f', '--family', type=click.STRING, multiple=True)
@click.option('-r', '--remove', type=click.BOOL, is_flag=True)
@click.pass_context
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
@click.argument('sha256', type=click.STRING)
@click.pass_context
def view(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag_link(api.tag_link_get(sha256))
