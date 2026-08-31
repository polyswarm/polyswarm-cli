import logging

import click

from polyswarm.client import utils

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
@click.option('-s', '--since', type=click.INT, default=86400,
              help='How far back in SECONDS to request results '
                   '(default: 86400 — 24h, the window the ruleset badge counts). '
                   'Pass 0 for no time filter at all.')
# click.INT matches every other id option in the CLI and rejects a typo before
# it reaches the server; IntRange(min=0) refuses a negative here rather than
# letting it silently mean unbounded.
@click.option('-i', '--livescan-id', type=click.INT,
              help="Scope the feed to one live hunt (a ruleset's Live Hunt Id, "
                   'a 17-digit number). Shows one community at a time, while '
                   'the badge counts all of them, so the counts need not match.')
@click.option('-m', '--max-results', type=click.IntRange(min=0),
              help='Stop after this many results. Unset or 0 means no bound — '
                   'every page, as before.')
@click.option('-r', '--rule-name', help='Filter results on this rule name.')
@click.option('-f', '--family', help='Filter hunt results based on the family name.')
@click.option('-l', '--polyscore-lower', help='Polyscore lower bound for the hunt results.')
@click.option('-u', '--polyscore-upper', help='Polyscore upper bound for the hunt results.')
@click.option('-p', '--private', is_flag=True, help='Filter results to only your private community.')
@click.pass_context
def live_results(ctx, since, livescan_id, max_results, rule_name, family,
                 polyscore_lower, polyscore_upper, private):
    """Show live-hunt results.

    `--livescan-id` scopes the feed to one live hunt — the drill-down for the
    per-ruleset new-results badge that `rules list` renders (the detail view
    deliberately does not carry it).

    The two do not have to agree, and a smaller feed is not a bug. The badge
    counts the hunt across EVERY community it runs in, public and private
    together; the feed shows one community at a time (this command always
    sends one — `--private` selects it). A hunt spanning both will show fewer
    rows here than the badge reports.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    kwargs = {}
    if livescan_id is not None:
        kwargs['livescan_id'] = livescan_id
    # Truthiness: 0 means unbounded, which is what omitting it already does.
    if max_results:
        kwargs['max_results'] = max_results
    for result in api.live_feed(
            since, rule_name=rule_name, family=family,
            polyscore_lower=polyscore_lower, polyscore_upper=polyscore_upper,
            community='private' if private else None, **kwargs):
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

