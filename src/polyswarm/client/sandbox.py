from __future__ import absolute_import
import logging

import click


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
    Submit an artifact by artifact id to the sandbox system.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for tasks in api.sandbox_instances(artifact_id):
        output.sandbox_tasks(tasks)


@sandbox.command('providers', short_help='List the names of available sandboxes.')
@click.pass_context
def sandbox_list(ctx):
    """
    List the names of available sandbox providers.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_providers(api.sandbox_providers())


@sandbox.command('lookup-id', short_help='Lookup the SandboxTasks based on the id.')
@click.argument('sandbox-task-id', nargs=-1, callback=utils.validate_id)
@click.pass_context
def task_status(ctx, sandbox_task_id):
    """
    Lookup the SandboxTasks based on the id returned when submitting.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    sandbox_task_ids = list(sandbox_task_id)

    for sandbox_task_id in sandbox_task_ids:
        output.sandbox_task(api.sandbox_task_status(sandbox_task_id))


@sandbox.command('lookup', short_help='Search the latest entry of SandboxTasks.')
@click.argument('sha256', type=click.STRING, required=True)
@click.argument('sandbox_', type=click.STRING, required=True)
@click.pass_context
def task_latest(ctx, sandbox_, sha256):
    """
    Lookup the latest entry of SandboxTasks by the tuple (hash, community, sandbox name).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_task(api.sandbox_task_latest(sha256, sandbox_))


@sandbox.command('search', short_help='Search for all the SandboxTasks.')
@click.argument('sha256', type=click.STRING, required=True)
@click.option('--sandbox', 'sandbox_', type=click.STRING)
@click.pass_context
def task_list(ctx, sha256, sandbox_):
    """
    Search for all the SandboxTasks identified by the tuple (hash, community, [sandbox], [start_date], [end_date]).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_tasks(api.sandbox_task_list(sha256, sandbox_))


@sandbox.command('my-tasks', short_help='Search for all the SandboxTasks.')
@click.argument('sha256', type=click.STRING, required=True)
@click.option('--sandbox', 'sandbox_', type=click.STRING)
@click.pass_context
def task_list(ctx, sha256, sandbox_):
    """
    Search for all the SandboxTasks identified by the tuple (hash, community, [sandbox], [start_date], [end_date]).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_tasks(api.sandbox_task_list(sha256, sandbox_))
