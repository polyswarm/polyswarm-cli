import logging

import click

from . import utils

logger = logging.getLogger(__name__)


@click.group(short_help='interact with live scans')
def live():
    pass


@click.group(short_help='interact with historical scans)')
def historical():
    pass


@live.command('create', short_help='Create a live hunt')
@click.argument('rule_file', type=click.File('r'))
@click.pass_context
def live_create(ctx, rule_file):
    api = ctx.obj['api']
    output = ctx.obj['output']
    rules = rule_file.read()
    result = api.live_create(rules)
    output.hunt(result)


@live.command('start', short_help='Start an existing live hunt')
@click.argument('hunt_id', nargs=-1, type=int)
@click.pass_context
def live_start(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = [dict(hunt_id=h) for h in hunt_id]
    args = [(True,)]*len(kwargs)
    for result in utils.parallel_executor(api.live_update, args_list=args, kwargs_list=kwargs):
        output.hunt(result)


@live.command('stop', short_help='Start an existing live hunt')
@click.argument('hunt_id', nargs=-1, type=int)
@click.pass_context
def live_stop(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = [dict(hunt_id=h) for h in hunt_id]
    args = [(False,)] * len(kwargs)
    for result in utils.parallel_executor(api.live_update, args_list=args, kwargs_list=kwargs):
        output.hunt(result)


@live.command('delete', short_help='Delete the live hunt associated with the given hunt_id')
@click.argument('hunt_id', nargs=-1, type=int)
@click.pass_context
def live_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = [dict(hunt_id=h) for h in hunt_id]
    for result in utils.parallel_executor(api.live_delete, kwargs_list=kwargs):
        output.hunt_deletion(result)


@live.command('list', short_help='List all live hunts performed')
@click.pass_context
def live_list(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_list()
    for hunt in result:
        output.hunt(hunt)


@live.command('results', short_help='Get results from live hunt')
@click.argument('hunt_id', type=int, required=False)
@click.option('-i', '--hunt-id', type=int, help='ID of the rule file (defaults to latest)')
@click.option('-s', '--since', type=click.INT, default=60,
              help='How far back in minutes to request results (default: 60, or all)')
@click.pass_context
def live_results(ctx, hunt_id, since):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_results(hunt_id, since=since)
    for hunt in result:
        output.hunt_result(hunt)


@historical.command('start', short_help='Start a new historical hunt')
@click.argument('rule_file', type=click.File('r'))
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
    result = api.historical_delete(hunt_id)
    output.hunt_deletion(result)


@historical.command('list', short_help='List all historical hunts performed')
@click.pass_context
def historical_list(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.historical_list()
    for hunt in result:
        output.hunt(hunt)


@historical.command('results', short_help='Get results from historical hunt')
@click.argument('hunt_id', type=int, required=False)
@click.pass_context
def historical_results(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.historical_results(hunt_id)
    for hunt in result:
        output.hunt_result(hunt)
