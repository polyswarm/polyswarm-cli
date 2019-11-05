import sys

import click
from polyswarm_api import exceptions

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

    try:
        result = api.live(rules)
        output.hunt_submission(result)
        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)
    except exceptions.InvalidYaraRules as e:
        output.invalid_rule(e)
        sys.exit(2)


@live.command('delete', short_help='Delete the live hunt associate with the given hunt_id')
@click.argument('hunt_id', type=int)
@click.pass_context
def live_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']

    try:
        result = api.live_delete(hunt_id)
        output.hunt_deletion(result)

        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)


@live.command('list', short_help='List all live hunts performed')
@click.pass_context
def live_list(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']

    try:
        result = api.live_list()
        output.hunt_list(result)
        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)


@click.option('-i', '--hunt-id', type=int, help='ID of the rule file (defaults to latest)')
@live.command('results', short_help='Get results from live hunt')
@click.option('-m', '--without-metadata', is_flag=True, default=False,
              help='Don\'t request artifact metadata.')
@click.option('-b', '--without-bounties', is_flag=True, default=False,
              help='Don\'t request bounties.')
@click.option('-s', '--since', type=click.INT, default=0,
              help='How far back in minutes to request results (default: 0, or all)')
@click.pass_context
def live_results(ctx, hunt_id, without_metadata, without_bounties, since):
    api = ctx.obj['api']
    output = ctx.obj['output']

    try:
        result = api.live_results(hunt_id, with_metadata=not without_metadata, with_instances=not without_bounties,
                                  since=since)
        output.hunt_result(result)
        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(1)


@click.argument('rule_file', type=click.File('r'))
@historical.command('start', short_help='Start a new historical hunt')
@click.pass_context
def historical_start(ctx, rule_file):
    api = ctx.obj['api']
    output = ctx.obj['output']

    rules = rule_file.read()

    try:
        result = api.historical(rules)
        output.hunt_submission(result)

        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)
    except exceptions.InvalidYaraRules as e:
        output.invalid_rule(e)
        sys.exit(2)


@historical.command('delete', short_help='Delete the historical hunt associate with the given hunt_id')
@click.argument('hunt_id', type=int)
@click.pass_context
def historical_delete(ctx, hunt_id):
    api = ctx.obj['api']
    output = ctx.obj['output']

    try:
        result = api.historical_delete(hunt_id)
        output.hunt_deletion(result)

        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)


@historical.command('list', short_help='List all historical hunts performed')
@click.pass_context
def historical_list(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']

    try:
        result = api.historical_list()
        output.hunt_list(result)

        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)


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

    try:
        result = api.historical_results(hunt_id, with_metadata=not without_metadata, with_instances=not without_bounties,
                                        since=since)

        output.hunt_result(result)

        if result.failed:
            sys.exit(1)
    except exceptions.UsageLimitsExceeded:
        output.usage_exceeded()
        sys.exit(2)
