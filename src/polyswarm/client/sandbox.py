from __future__ import absolute_import
import logging

import click

from polyswarm_api import settings

from polyswarm.client import utils

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with the Polyswarm sandbox system.')
def sandbox():
    pass


@sandbox.command('submit', short_help='Submit a scanned artifact to be run through sandbox.')
@click.argument('artifact-id', nargs=-1, callback=utils.validate_id)
@click.pass_context
def submit(ctx, artifact_id):
    """
    Submit an artifact by sha256 to the sandbox system.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for instance in api.sandbox_instances(artifact_id):
        output.sandbox_result(instance)


@sandbox.command('list', short_help='List the names of available sandboxes.')
@click.pass_context
def sandbox_list(ctx):
    """
    List the names of available sandboxes.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_list(api.sandbox_list())
