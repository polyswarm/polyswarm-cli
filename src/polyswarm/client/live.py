from __future__ import absolute_import
import logging

import click

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with live hunts.')
def live():
    pass


@live.command('start', short_help='Create a live hunt.')
@click.argument('rule_id', type=click.INT)
@click.pass_context
def live_start(ctx, rule_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_start(rule_id)
    output.ruleset(result)


@live.command('stop', short_help='Stop a live hunt.')
@click.argument('rule_id', type=click.INT)
@click.pass_context
def live_stop(ctx, rule_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_stop(rule_id)
    output.ruleset(result)


@live.command('feed', short_help='Get results from live hunt.')
@click.option('-s', '--since', type=click.INT, default=1440,
              help='How far back in seconds to request results (default: 1440).')
@click.option('-r', '--rule-name', help='Filter results on this rule name.')
@click.pass_context
def live_results(ctx, since, rule_name):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for result in api.live_feed(since, rule_name):
        output.live_result(result)


@live.command('result', short_help='Get results from live hunt.')
@click.argument('result-id', type=click.INT)
@click.pass_context
def live_results(ctx, result_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.live_result(api.live_result(result_id))
