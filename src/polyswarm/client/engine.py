from __future__ import absolute_import
import logging

import click

logger = logging.getLogger(__name__)


@click.group(short_help="Interact with engines.")
def engine():
    pass


@engine.group(short_help="Interact with engine's votes.")
def votes():
    pass


@engine.group(short_help="Interact with engine's assertions.")
def assertions():
    pass


@assertions.command('create', short_help='Create a new bundle with the consolidated assertions data.')
@click.argument('engine-id', type=click.STRING)
@click.argument('date-start', type=click.STRING)
@click.argument('date-end', type=click.STRING)
@click.pass_context
def assertions_create(ctx, engine_id, date_start, date_end):
    """
    Create a new bundle with the consolidated assertions data for the provided
    period of time.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.assertions_create(engine_id, date_start, date_end)
    output.assertions(result)


@assertions.command('get', short_help='Get an assertions bundle.')
@click.argument('assertions-job-id', type=click.INT)
@click.pass_context
def assertions_get(ctx, assertions_job_id):
    """
    Get the assertions bundle for the given bundle id.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.assertions_get(assertions_job_id)
    output.assertions(result)


@votes.command('create', short_help='Create a new bundle with the consolidated votes data.')
@click.argument('engine-id', type=click.STRING)
@click.argument('date-start', type=click.STRING)
@click.argument('date-end', type=click.STRING)
@click.pass_context
def votes_create(ctx, engine_id, date_start, date_end):
    """
    Create a new bundle with the consolidated votes data for the provided
    period of time.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.votes_create(engine_id, date_start, date_end)
    output.votes(result)


@votes.command('get', short_help='Get a votes bundle.')
@click.argument('votes-job-id', type=click.INT)
@click.pass_context
def votes_get(ctx, votes_job_id):
    """
    Get the votes bundle for the given bundle id.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.votes_get(votes_job_id)
    output.votes(result)
