import click


@click.group(short_help='interact with live scans')
def live():
    pass


@click.group(short_help='interact with historical scans)')
def historical():
    pass


@click.argument('rule_file', type=click.File('r'))
@live.command('start', short_help='Start a new live hunt')
@click.pass_context
def live_start(ctx, rule_file):
    api = ctx.obj['api']
    output = ctx.obj['output']
    rules = rule_file.read()
    result = api.live_create(rules)
    output.hunt(result)


@live.command('delete', short_help='Delete the live hunt associate with the given hunt_id')
@click.argument('hunt_id', type=int)
@click.pass_context
def live_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.delete_live_hunt(hunt_id)
    output.hunt_deletion(result)


@live.command('list', short_help='List all live hunts performed')
@click.pass_context
def live_list(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_list()
    output.hunt_list(result)


@click.option('-i', '--hunt-id', type=int, help='ID of the rule file (defaults to latest)')
@live.command('results', short_help='Get results from live hunt')
@click.argument('hunt_id', type=int, required=False)
@click.option('-s', '--since', type=click.INT, default=60,
              help='How far back in minutes to request results (default: 60, or all)')
@click.pass_context
def live_results(ctx, hunt_id, since):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_results(hunt_id, since=since)
    for live_hunt in result:
        output.hunt_result(live_hunt)


@click.argument('rule_file', type=click.File('r'))
@historical.command('start', short_help='Start a new historical hunt')
@click.pass_context
def historical_start(ctx, rule_file):
    api = ctx.obj['api']
    output = ctx.obj['output']
    rules = rule_file.read()
    result = api.historical_create(rules)
    output.hunt(result)


@historical.command('delete', short_help='Delete the historical hunt associate with the given hunt_id')
@click.argument('hunt_id', type=int)
@click.pass_context
def historical_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.delete_historical_hunt(hunt_id)
    output.hunt_deletion(result)


@historical.command('list', short_help='List all historical hunts performed')
@click.pass_context
def historical_list(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.historical_list()
    output.hunt_list(result)


@click.option('-i', '--hunt-id', type=int, help='ID of the rule file (defaults to latest)')
@click.option('-m', '--without-metadata', is_flag=True, default=False,
              help='Don\'t request artifact metadata.')
@click.option('-b', '--without-bounties', is_flag=True, default=False,
              help='Don\'t request bounties.')
@click.option('-s', '--since', type=click.INT, default=0,
              help='How far back in minutes to request results (default: 0, or all)')
@historical.command('results', short_help='Get results from historical hunt')
@click.pass_context
def historical_results(ctx, hunt_id, without_metadata, without_bounties, since):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.historical_results(hunt_id, with_metadata=not without_metadata, with_instances=not without_bounties,
                                    since=since)
    output.hunt_result(result)
