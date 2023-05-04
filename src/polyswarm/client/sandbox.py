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

    for tasks in api.sandbox_instances(artifact_id):
        output.sandbox_tasks(tasks)


@sandbox.command('list', short_help='List the names of available sandboxes.')
@click.pass_context
def sandbox_list(ctx):
    """
    List the names of available sandboxes.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_list(api.sandbox_list())


@sandbox.command('status', short_help='Lookup the last updated time of the sandbox metadata for an instance.')
@click.argument('scan-id', nargs=-1, callback=utils.validate_id)
@click.pass_context
def status(ctx, scan_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    scan_ids = list(scan_id)

    for instance in api.scan_lookup(scan_ids):
        output.artifact_metadata(instance, only=['cape_sandbox_v2', 'triage_sandbox_v0'])

@sandbox.command('task-status', short_help='Lookup the status of a sandbox task by id.')
@click.argument('sandbox-task-id', nargs=-1, callback=utils.validate_id)
@click.pass_context
def task_status(ctx, sandbox_task_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    sandbox_task_ids = list(sandbox_task_id)

    for sandbox_task_id in sandbox_task_ids:
        output.sandbox_task(api.sandbox_task_status(sandbox_task_id))

@sandbox.command('task-latest', short_help='Lookup the latest sandbox task by sha256.')
@click.argument('sha256', type=click.STRING, required=True)
@click.option('--sandbox', type=click.STRING)
@click.pass_context
def task_latest(ctx, sha256, sandbox):
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_task(api.sandbox_task_latest(sha256, sandbox))

@sandbox.command('task-list', short_help='List the sandbox tasks for a given sha256.')
@click.argument('sha256', type=click.STRING, required=True)
@click.option('--sandbox', type=click.STRING)
@click.pass_context
def task_list(ctx, sha256, sandbox):
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_tasks(api.sandbox_task_list(sha256, sandbox))
