import logging
from os import path

import click

from . import utils

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with live hunts.')
def live():
    pass


@click.group(short_help='Interact with historical hunts.')
def historical():
    pass


@live.command('create', short_help='Create a live hunt.')
@click.argument('rule_file', type=click.File('r'), required=False)
@click.option('-r', '--rule-id', type=click.INT, help='If provided, create the live hunt from the existing ruleset.')
@click.option('-d', '--disabled', is_flag=True, help='If provided, create the live hunt with active=False.')
@click.option('-n', '--name', help='Explicitly set the ruleset name for this hunt.')
@click.pass_context
def live_create(ctx, rule_file, rule_id, disabled, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    params = {}
    if rule_file:
        rule = rule_file.read()
        params['ruleset_name'] = path.basename(rule_file.name)
    elif rule_id:
        rule = rule_id
    else:
        raise click.exceptions.BadArgumentUsage('One of rule_file argument or --rule-id option should be provided.')
    if name:
        params['ruleset_name'] = name
    params['active'] = not disabled
    result = api.live_create(rule, **params)
    output.hunt(result)


@live.command('start', short_help='Start an existing live hunt.')
@click.argument('hunt_id', nargs=-1, type=click.INT)
@click.pass_context
def live_start(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = [dict(hunt=h) for h in hunt_id]
    args = [(True,)]*len(kwargs)
    for result in utils.parallel_executor(api.live_update, args_list=args, kwargs_list=kwargs):
        output.hunt(result)


@live.command('stop', short_help='Start an existing live hunt.')
@click.argument('hunt_id', nargs=-1, type=click.INT)
@click.pass_context
def live_stop(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = [dict(hunt=h) for h in hunt_id] if hunt_id else [dict(hunt_id=None)]
    args = [(False,)] * len(kwargs)
    for result in utils.parallel_executor(api.live_update, args_list=args, kwargs_list=kwargs):
        output.hunt(result)


@live.command('delete', short_help='Delete the live hunt associated with the given hunt_id.')
@click.argument('hunt_id', nargs=-1, type=click.INT)
@click.pass_context
def live_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = [dict(hunt=h) for h in hunt_id]
    for result in utils.parallel_executor(api.live_delete, kwargs_list=kwargs):
        output.hunt_deletion(result)


@live.command('list', short_help='List all live hunts performed.')
@click.option('-s', '--since', type=click.INT, help='How far back in seconds to request results.')
@click.option('-a', '--all', 'all_', is_flag=True, help='Request all live hunts ever created.')
@click.pass_context
def live_list(ctx, since, all_):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = {}
    if since is not None:
        kwargs['since'] = since
    if all_ is not None:
        kwargs['all_'] = all_
    result = api.live_list(**kwargs)
    for hunt in result:
        output.hunt(hunt)


@live.command('results', short_help='Get results from live hunt.')
@click.argument('hunt_id', nargs=-1, type=click.INT)
@click.option('-s', '--since', type=click.INT, default=1440,
              help='How far back in seconds to request results (default: 1440).')
@click.option('-t', '--tag', help='Filter results on this tag.')
@click.option('-r', '--rule-name', help='Filter results on this rule name.')
@click.pass_context
def live_results(ctx, hunt_id, since, tag, rule_name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    args = [(h,) for h in hunt_id] if hunt_id else [(None,)]
    kwargs = [dict(since=since, tag=tag, rule_name=rule_name)]*len(args)
    for result in utils.parallel_executor_iterable_results(api.live_results, args_list=args, kwargs_list=kwargs):
        output.hunt_result(result)


@historical.command('start', short_help='Start a new historical hunt.')
@click.argument('rule_file', type=click.File('r'), required=False)
@click.option('-r', '--rule-id', type=click.INT, help='If provided, create the historical hunt from the existing ruleset.')
@click.option('-n', '--name', help='Explicitly set the ruleset name for this hunt.')
@click.pass_context
def historical_start(ctx, rule_file, rule_id, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    params = {}
    if rule_file:
        rule = rule_file.read()
        params['ruleset_name'] = path.basename(rule_file.name)
    elif rule_id:
        rule = rule_id
    else:
        raise click.exceptions.BadArgumentUsage('One of rule_file argument or --rule-id option should be provided.')
    if name:
        params['ruleset_name'] = name
    result = api.historical_create(rule, **params)
    output.hunt(result)


@historical.command('delete', short_help='Delete the historical hunt associated with the given hunt_id.')
@click.argument('hunt_id', nargs=-1, type=click.INT)
@click.pass_context
def historical_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = [dict(hunt=h) for h in hunt_id]
    for result in utils.parallel_executor(api.historical_delete, kwargs_list=kwargs):
        output.hunt_deletion(result)


@historical.command('list', short_help='List all historical hunts performed.')
@click.option('-s', '--since', type=click.INT, help='How far back in seconds to request results.')
@click.pass_context
def historical_list(ctx, since):
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = {}
    if since is not None:
        kwargs['since'] = since
    result = api.historical_list(**kwargs)
    for hunt in result:
        output.hunt(hunt)


@historical.command('results', short_help='Get results from historical hunt.')
@click.argument('hunt_id', nargs=-1, type=click.INT)
@click.option('-t', '--tag', help='Filter results on this tag.')
@click.option('-r', '--rule-name', help='Filter results on this rule name.')
@click.pass_context
def historical_results(ctx, hunt_id, tag, rule_name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    args = [(h,) for h in hunt_id] if hunt_id else [(None,)]
    kwargs = [dict(tag=tag, rule_name=rule_name)] * len(args)
    for result in utils.parallel_executor_iterable_results(api.historical_results, args_list=args, kwargs_list=kwargs):
        output.hunt_result(result)
