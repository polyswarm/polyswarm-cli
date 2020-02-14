import click


@click.group(short_help='Interact with Tag links in Polyswarm.')
def link():
    pass


@link.command('create', short_help='Create a tag.')
@click.argument('sha256', type=click.STRING)
@click.option('-t', '--tag', type=click.STRING, multiple=True)
@click.option('-f', '--family', type=click.STRING, multiple=True)
@click.pass_context
def create(ctx, sha256, tag, family):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag_link(api.tag_link_create(sha256, tags=tag, families=family))


@link.command('delete', short_help='Delete a tag.')
@click.argument('sha256', type=click.STRING)
@click.pass_context
def delete(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag_link(api.tag_link_delete(sha256))


@link.command('update', short_help='Update a tag.')
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


@link.command('view', short_help='View a tag.')
@click.argument('sha256', type=click.STRING)
@click.pass_context
def view(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag_link(api.tag_link_get(sha256))
