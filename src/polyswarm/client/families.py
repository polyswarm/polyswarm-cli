from __future__ import absolute_import
import click


@click.group(short_help='Interact with Malware Families in Polyswarm.')
def family():
    pass


@family.command('update', short_help='Mark a family as emerging.')
@click.argument('name', type=click.STRING, required=True)
@click.option('-e', '--emerging', type=click.BOOL)
@click.pass_context
def update(ctx, name, emerging):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.family(api.family_update(name, emerging=emerging))


@family.command('create', short_help='Create a family.')
@click.argument('name', type=click.STRING, required=True)
@click.pass_context
def create(ctx, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.family(api.family_create(name))


@family.command('delete', short_help='Delete a family.')
@click.argument('name', type=click.STRING, required=True)
@click.pass_context
def delete(ctx, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.family(api.family_delete(name))


@family.command('view', short_help='View a family.')
@click.argument('name', type=click.STRING, required=True)
@click.pass_context
def view(ctx, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.family(api.family_get(name))


@family.command('list', short_help='List all families.')
@click.pass_context
def list_rules(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for family in api.family_list():
        output.family(family)
