from __future__ import absolute_import
import click


@click.group(short_help='Interact with Yara Rules stored in Polyswarm.')
def event():
    pass


@event.command('list', short_help='List all events.')
@click.pass_context
def list_rules(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for event in api.event_list():
        output.event(event)
