import click


@click.group(short_help='Interact with Tags in Polyswarm.')
def tag():
    pass


@tag.command('create', short_help='Create a tag.')
@click.argument('name', type=click.STRING)
@click.pass_context
def create(ctx, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_create(name))


@tag.command('delete', short_help='Delete a tag.')
@click.argument('name', type=click.STRING)
@click.pass_context
def delete(ctx, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_delete(name))


@tag.command('view', short_help='View a tag.')
@click.argument('name', type=click.STRING)
@click.pass_context
def view(ctx, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_get(name))