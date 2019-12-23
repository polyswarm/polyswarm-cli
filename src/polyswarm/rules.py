import click


@click.group(short_help='Interact with Yara Rules stored in Polyswarm')
def rules():
    pass


@rules.command('create', short_help='Create a ruleset')
@click.argument('rule_name', type=str)
@click.argument('rule_file', type=click.File('r'))
@click.option('-d', '--description', type=str, help='Description of the ruleset')
@click.pass_context
def create(ctx, rule_name, rule_file, description):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.rule_set(api.rule_set_create(rule_name, rule_file.read(), description=description))


@rules.command('delete', short_help='Delete a ruleset')
@click.argument('rule_id', type=int)
@click.pass_context
def delete(ctx, rule_id):
    raise NotImplementedError()


@rules.command('list', short_help='List all rulesets')
@click.pass_context
def list(ctx):
    raise NotImplementedError()


@rules.command('update', short_help='Update a ruleset')
@click.option('-n', '--name', type=str, help='Name of the ruleset')
@click.option('-f', '--file', type=click.File('r'), help='File containing the Yara rules')
@click.pass_context
def update(ctx, name, file):
    raise NotImplementedError()


@rules.command('view', short_help='View a ruleset')
@click.argument('rule_id', type=int)
@click.pass_context
def view(ctx, rule_id):
    raise NotImplementedError()

