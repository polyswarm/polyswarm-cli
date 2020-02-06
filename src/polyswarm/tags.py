import click


@click.group(short_help='Interact with Tags in Polyswarm.')
def tags():
    pass


@tags.command('create', short_help='Create a tag.')
@click.argument('sha256', type=click.STRING)
@click.option('-t', '--tag', type=click.STRING, multiple=True)
@click.option('-f', '--family', type=click.STRING, multiple=True)
@click.pass_context
def create(ctx, sha256, tag, family):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_create(sha256, tags=tag, families=family))


@tags.command('delete', short_help='Delete a tag.')
@click.argument('sha256', type=click.STRING)
@click.pass_context
def delete(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_delete(sha256))


@tags.command('list', short_help='List all tags.')
@click.argument('sha256', type=click.STRING)
@click.pass_context
def list_rules(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for tag in api.tag_list(sha256):
        output.tag(tag)


@tags.command('update', short_help='Update a tag.')
@click.argument('sha256', type=click.STRING)
@click.option('-t', '--tag', type=click.STRING, multiple=True)
@click.option('-f', '--family', type=click.STRING, multiple=True)
@click.option('-r', '--remove', type=click.BOOL, is_flag=True)
@click.pass_context
def update(ctx, sha256, tag, family, remove):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_update(
        sha256,
        tags=tag,
        families=family,
        remove=remove,
    ))


@tags.command('view', short_help='View a tag.')
@click.argument('sha256', type=click.STRING)
@click.pass_context
def view(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_get(sha256))
