from __future__ import absolute_import
import logging
from os import path

import click

from polyswarm.client import utils

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
@utils.any_provided('rule_file', 'rule_id')
def live_create(ctx, rule_file, rule_id, disabled, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    params = {}
    if rule_file:
        rule = rule_file.read()
        params['ruleset_name'] = path.basename(rule_file.name)
    elif rule_id:
        rule = rule_id
    if name:
        params['ruleset_name'] = name
    params['active'] = not disabled
    result = api.live_create(rule, **params)
    output.hunt(result)


@live.command('start', short_help='Start an existing live hunt.')
@click.argument('hunt_id', nargs=-1, type=click.INT, required=True)
@click.pass_context
def live_start(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for result in api.live_start(hunt_id):
        output.hunt(result)


@live.command('stop', short_help='Stop an existing live hunt.')
@click.argument('hunt_id', nargs=-1, type=click.INT)
@click.pass_context
def live_stop(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for result in api.live_stop(hunt_id):
        output.hunt(result)


@live.command('delete', short_help='Delete the live hunt associated with the given hunt_id.')
@click.argument('hunt_id', nargs=-1, type=click.INT)
@click.pass_context
def live_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for result in api.live_delete_multiple(hunt_id):
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
@click.argument('hunt_id', nargs=-1, type=click.INT, required=True)
@click.option('-s', '--since', type=click.INT, default=1440,
              help='How far back in seconds to request results (default: 1440).')
@click.option('-t', '--tag', help='Filter results on this tag.')
@click.option('-r', '--rule-name', help='Filter results on this rule name.')
@click.pass_context
def live_results(ctx, hunt_id, since, tag, rule_name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for result in api.live_results_multiple(hunt_id, since, tag, rule_name):
        output.hunt_result(result)


@historical.command('start', short_help='Start a new historical hunt.')
@click.argument('rule_file', type=click.File('r'), required=False)
@click.option('-r', '--rule-id', type=click.INT, help='If provided, create the historical hunt from the existing ruleset.')
@click.option('-n', '--name', help='Explicitly set the ruleset name for this hunt.')
@click.pass_context
@utils.any_provided('rule_file', 'rule_id')
def historical_start(ctx, rule_file, rule_id, name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    params = {}
    if rule_file:
        rule = rule_file.read()
        params['ruleset_name'] = path.basename(rule_file.name)
    elif rule_id:
        rule = rule_id
    if name:
        params['ruleset_name'] = name
    result = api.historical_create(rule, **params)
    output.hunt(result)


@historical.command('delete', short_help='Delete the historical hunt associated with the given hunt_id.')
@click.argument('hunt_id', nargs=-1, type=click.INT, required=True)
@click.pass_context
def historical_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for result in api.historical_delete_multiple(hunt_id):
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
@click.argument('hunt_id', nargs=-1, type=click.INT, required=True)
@click.option('-t', '--tag', help='Filter results on this tag.')
@click.option('-r', '--rule-name', help='Filter results on this rule name.')
@click.pass_context
def historical_results(ctx, hunt_id, tag, rule_name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for result in api.historical_results_multiple(hunt_id, tag, rule_name):
        output.hunt_result(result)
