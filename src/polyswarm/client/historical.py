from __future__ import absolute_import
import logging
from os import path

import click

from polyswarm.client import utils

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with historical hunts.')
def historical():
    pass


@historical.command('view', short_help='View the historical hunt associated with the given hunt_id.')
@click.argument('hunt_id', type=click.INT)
@click.pass_context
def historical_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.hunt_deletion(api.historical_get(hunt_id))


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


@historical.command('delete-list', short_help='Delete a list of historical hunts.')
@click.argument('historical-ids', nargs=-1, type=click.INT, required=True)
@click.pass_context
def historical_list(ctx, historical_ids):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.historical_delete_list(historical_ids)
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
        output.historical_result(result)
