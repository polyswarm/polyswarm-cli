from __future__ import absolute_import
import click

from polyswarm.client import utils


@click.group(short_help='Interact with Yara Rules stored in Polyswarm.')
def rules():
    pass


@rules.command('create', short_help='Create a ruleset.')
@click.argument('rule_name', type=str)
@click.argument('rule_file', type=click.File('r'), required=True)
@click.option('-d', '--description', type=str, help='Description of the ruleset.')
@click.pass_context
def create(ctx, rule_name, rule_file, description):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.ruleset(api.ruleset_create(rule_name, rule_file.read(), description=description))


@rules.command('delete', short_help='Delete a ruleset.')
@click.argument('rule_id', type=click.INT, required=True)
@click.pass_context
def delete(ctx, rule_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.ruleset(api.ruleset_delete(rule_id))


@rules.command('list', short_help='List all rulesets.')
@click.pass_context
def list_rules(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for ruleset in api.ruleset_list():
        output.ruleset(ruleset)


@rules.command('update', short_help='Update a ruleset.')
@click.argument('rule_id', type=click.INT, required=True)
@click.option('-n', '--name', type=str, help='Name of the ruleset.')
@click.option('-f', '--file', type=click.File('r'), help='File containing the Yara rules.')
@click.option('-d', '--description', type=str, help='Description of the ruleset.')
@click.pass_context
@utils.any_provided('name', 'file', 'description')
def update(ctx, rule_id, name, file, description):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.ruleset(api.ruleset_update(
        rule_id,
        name=name if name else None,
        rules=file.read() if file else None,
        description=description if description else None,
    ))


@rules.command('view', short_help='View a ruleset.')
@click.argument('rule_id', type=click.INT, required=True)
@click.pass_context
def view(ctx, rule_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.ruleset(api.ruleset_get(rule_id), contents=True)


