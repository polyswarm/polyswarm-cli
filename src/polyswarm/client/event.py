import click


@click.group(short_help='Interact with Yara Rules stored in Polyswarm.')
def activity():
    pass


@activity.command('list', short_help='List all activity.')
@click.option("--filter", "-f", multiple=True, type=click.STRING)
@click.pass_context
def list_rules(ctx, filter):
    api = ctx.obj['api']
    output = ctx.obj['output']
    filters = {v[0]: v[2] for v in iter(entry.partition('=') for entry in filter)}
    for event in api.event_list(**filters):
        output.event(event)
