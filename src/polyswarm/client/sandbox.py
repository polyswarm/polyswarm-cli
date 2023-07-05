from __future__ import absolute_import
import logging

import click


from polyswarm.client import utils

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with the Polyswarm sandbox system.')
def sandbox():
    pass


@sandbox.command('instance', short_help='Submit an existing artifact by id to be sandboxed.')
@click.argument('provider_slug', type=click.STRING)
@click.argument('artifact-id', nargs=-1, callback=utils.validate_id)
@click.option('--vm_slug', 'vm_slug', type=click.STRING)
@click.pass_context
def submit(ctx, provider_slug, artifact_id, vm_slug):
    """
    Submit an artifact by artifact id to be sandboxed.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for tasks in api.sandbox_instances(artifact_id, provider_slug=provider_slug, vm_slug=vm_slug):
        output.sandbox_task(tasks)


@sandbox.command('file', short_help='Submit a local file to be sandboxed.')
@click.argument('sandbox', type=click.STRING)
@click.argument('path', type=click.Path(exists=True), required=True)
@click.option('--vm_slug', 'vm_slug', type=click.STRING)
@click.pass_context
def file(ctx, path, sandbox, vm_slug):
    """
    Submit a local file to be sandboxed.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_task(api.sandbox_file(path, sandbox, vm_slug))


@sandbox.command('providers', short_help='List the names of available sandboxes.')
@click.pass_context
def sandbox_list(ctx):
    """
    List the names of available sandbox providers.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_providers(api.sandbox_providers())


@sandbox.command('lookup-id', short_help='Lookup the sandbox results based on the id.')
@click.argument('sandbox-task-id', nargs=-1, callback=utils.validate_id)
@click.pass_context
def task_status(ctx, sandbox_task_id):
    """
    Lookup the sandbox results based on the id returned when submitting.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    sandbox_task_ids = list(sandbox_task_id)

    for sandbox_task_id in sandbox_task_ids:
        output.sandbox_task(api.sandbox_task_status(sandbox_task_id))


@sandbox.command('lookup', short_help='Lookup the latest sandbox results for a hash.')
@click.argument('sandbox_', type=click.STRING, required=True)
@click.argument('sha256', type=click.STRING, required=True)
@click.pass_context
def task_latest(ctx, sha256, sandbox_):
    """
    Lookup the latest results of sandbox data for the tuple (hash, community, sandbox name).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_task(api.sandbox_task_latest(sha256, sandbox_))


@sandbox.command('search', short_help='Search for all the sandbox results for a hash.')
@click.argument('sha256', type=click.STRING, required=True)
@click.option('--sandbox', 'sandbox_', type=click.STRING)
@click.option('--start-date', 'start_date', type=click.STRING)
@click.option('--end-date', 'end_date', type=click.STRING)
@click.option('--status', 'status', type=click.STRING)
@click.pass_context
def task_list(ctx, sha256, sandbox_, start_date, end_date, status):
    """
    Search for all the sandbox results identified by the tuple (hash, community, [sandbox], [start_date], [end_date], [status]).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for task in api.sandbox_task_list(sha256, sandbox=sandbox_, start_date=start_date, end_date=end_date, status=status):
        output.sandbox_task(task)


@sandbox.command('my-tasks', short_help='Search for all the sandbox results created by my account or team.')
@click.option('--sandbox', 'sandbox_', type=click.STRING)
@click.option('--start-date', type=click.STRING)
@click.option('--end-date', type=click.STRING)
@click.pass_context
def my_task_list(ctx, sandbox_, start_date, end_date):
    """
    List the sandbox results associated with my account/team for the tuple (community, [sandbox], [start_date], [end_date])
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for task in api.sandbox_my_tasks_list(sandbox=sandbox_, start_date=start_date, end_date=end_date):
        output.sandbox_task(task)
