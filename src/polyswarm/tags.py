import click


@click.group(short_help='Interact with Tags in Polyswarm.')
def tags():
    pass


@tags.command('create', short_help='Create a tag.')
@click.argument('sha256', type=click.STRING, help='Hash of the file to tag.')
@click.argument('tag_type', type=click.STRING, help='Type of the tag.')
@click.argument('tag_value', type=click.STRING, help='Value of the tag.')
@click.pass_context
def create(ctx, sha256, tag_type, tag_value):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_create(sha256, tag_type, tag_value))


@tags.command('delete', short_help='Delete a tag.')
@click.argument('tag_id', type=click.INT, help='Id of the tag.')
@click.pass_context
def delete(ctx, tag_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_delete(tag_id))


@tags.command('list', short_help='List all tags.')
@click.argument('sha256', type=click.STRING, help='Hash of the file to to fetch associated tags.')
@click.pass_context
def list_rules(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for tag in api.tag_list(sha256):
        output.tag(tag)


@tags.command('update', short_help='Update a tag.')
@click.argument('tag_id', type=click.INT, help='Id of the tag.')
@click.option('--tag-type', type=click.STRING, help='Type of the tag.')
@click.option('--tag-value', type=click.STRING, help='Value of the tag.')
@click.pass_context
def update(ctx, tag_id, tag_type, tag_value):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_update(
        tag_id,
        tag_type=tag_type if tag_type else None,
        tag_value=tag_value if tag_value else None,
    ))


@tags.command('view', short_help='View a tag.')
@click.argument('tag_id', type=click.INT, help='Id of the tag.')
@click.pass_context
def view(ctx, tag_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.tag(api.tag_get(tag_id))
