import logging

import click

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with live hunts.')
def live():
    pass


@live.command('start', short_help='Create a live hunt.')
@click.argument('ruleset-id', type=click.INT)
@click.pass_context
def live_start(ctx, ruleset_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_start(ruleset_id)
    output.ruleset(result)


@live.command('stop', short_help='Stop a live hunt.')
@click.argument('ruleset-id', type=click.INT)
@click.pass_context
def live_stop(ctx, ruleset_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_stop(ruleset_id)
    output.ruleset(result)


@live.command('feed', short_help='Get results from live hunt.')
@click.option('-s', '--since', type=click.INT, default=1440,
              help='How far back in seconds to request results (default: 1440).')
@click.option('-r', '--rule-name', help='Filter results on this rule name.')
@click.option('-f', '--family', help='Filter hunt results based on the family name.')
@click.option('-l', '--polyscore-lower', help='Polyscore lower bound for the hunt results.')
@click.option('-u', '--polyscore-upper', help='Polyscore upper bound for the hunt results.')
@click.option('-p', '--private', is_flag=True, help='Filter results to only your private community.')
@click.pass_context
def live_results(ctx, since, rule_name, family, polyscore_lower, polyscore_upper, private):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for result in api.live_feed(
            since, rule_name=rule_name, family=family,
            polyscore_lower=polyscore_lower, polyscore_upper=polyscore_upper, community='private' if private else None):
        output.live_result(result)


@live.command('result', short_help='Get results from live hunt.')
@click.argument('result-id', type=click.INT)
@click.pass_context
def live_results(ctx, result_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.live_result(api.live_result(result_id))


@live.command('results-delete', short_help='Delete a list of live results.')
@click.argument('result-ids', nargs=-1, type=click.INT, required=True)
@click.pass_context
def historical_results_delete(ctx, result_ids):
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.live_feed_delete(result_ids)
    for hunt in result:
        output.live_result(hunt)

