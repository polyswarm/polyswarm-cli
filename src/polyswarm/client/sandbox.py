import logging

import click


from polyswarm.client import utils
from polyswarm.utils import is_url

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with the Polyswarm sandbox system.')
def sandbox():
    pass


@sandbox.command('instance', short_help='Submit an existing artifact by id to be sandboxed.')
@click.argument('provider_slug', type=click.STRING)
@click.argument('artifact-id', nargs=-1, callback=utils.validate_id)
@click.option('--vm_slug', 'vm_slug', type=click.STRING)
@click.option('--internet-disabled', 'internet_disabled', type=click.BOOL, is_flag=True, default=False)
@click.pass_context
def submit(ctx, provider_slug, artifact_id, vm_slug, internet_disabled):
    """
    Submit an artifact by artifact id to be sandboxed.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for tasks in api.sandbox_instances(
            artifact_id, provider_slug=provider_slug, vm_slug=vm_slug, network_enabled=not internet_disabled):
        output.sandbox_task(tasks)


@sandbox.command('file', short_help='Submit a local file to be sandboxed.')
@click.argument('provider', type=click.STRING)
@click.argument('path', type=click.Path(exists=True), required=True)
@click.option('--vm_slug', 'vm_slug', type=click.STRING)
@click.option('--internet-disabled', 'internet_disabled', type=click.BOOL, is_flag=True, default=False)
@click.option('-z', '--is-zip', type=click.BOOL, is_flag=True,
              help='Will handle the provided file as a zip and decompress server-side.')
@click.option('-p', '--zip-password', type=click.STRING,
              help='Will use this password to decompress the zip file. If provided, will handle the file as a zip.')
@click.pass_context
def file(ctx, path, provider, vm_slug, internet_disabled, is_zip, zip_password):
    """
    Submit a local file to be sandboxed.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    if is_zip or zip_password:
        preprocessing = {'type': 'zip'}
        if zip_password:
            preprocessing['password'] = zip_password
    else:
        preprocessing = None
    output.sandbox_task(api.sandbox_file(path, provider, vm_slug, network_enabled=not internet_disabled,
                                         preprocessing=preprocessing))


@sandbox.command('url', short_help='Submit a url to be sandboxed.')
@click.argument('provider', type=click.STRING)
@click.argument('url', type=click.STRING, required=False)
@click.option('--qrcode-file', type=click.Path(exists=True),
              help='QR Code image file with the URL as payload.')
@click.option('--vm_slug', 'vm_slug', type=click.STRING,
              help="The slug of the Virtual machine to use. Check the list "
                   "of available virtual machines with the providers command.")
@click.option('--browser', 'browser', type=click.STRING,
              help="Which browser to use, e.g. 'firefox' or 'edge'.")
@click.pass_context
@utils.any_provided('url', 'qrcode_file')
def url(ctx, url, qrcode_file, provider, vm_slug, browser):
    """
    Submit an url to be sandboxed.
    """
    if qrcode_file:
        if url:
            raise click.BadArgumentUsage('--qrcode-file cannot be used with URL.')
        preprocessing = {'type': 'qrcode'}
    else:
        preprocessing = None
        if url and not is_url(url):
            raise click.BadArgumentUsage(f'URL "{url}" is not valid. '
                                         'Make sure the protocol "https://" or "http://" is set.')
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.sandbox_task(api.sandbox_url(url,
                                        provider,
                                        vm_slug,
                                        artifact=qrcode_file,
                                        artifact_name=qrcode_file,
                                        preprocessing=preprocessing,
                                        browser=browser))


@sandbox.command('providers', short_help='List the names of available sandbox providers and VMs.')
@click.pass_context
def sandbox_list(ctx):
    """
    List the names of available sandbox providers, and the virtual machines supported by each.
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
@click.argument('provider', type=click.STRING, required=True)
@click.argument('sha256', type=click.STRING, required=True)
@click.pass_context
def task_latest(ctx, sha256, provider):
    """
    Lookup the latest results of sandbox data for the tuple (SHA256, community, sandbox PROVIDER name).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sandbox_task(api.sandbox_task_latest(sha256, provider))


@sandbox.command('search', short_help='Search for all the sandbox results for a hash.')
@click.argument('sha256', type=click.STRING, required=True)
@click.option('--provider', type=click.STRING, help='Filter by slug of the sandbox provider')
@click.option('--start-date', 'start_date', type=click.STRING,
              help='Tasks created the day passed or after (ISO format).')
@click.option('--end-date', 'end_date', type=click.STRING,
              help='Tasks created the day passed or before (ISO format).')
@click.option('--status', 'status', type=click.STRING)
@click.option('--account-id', 'account_id', type=click.STRING)
@click.pass_context
def task_list(ctx, sha256, provider, start_date, end_date, status, account_id):
    """
    Search for all the sandbox results identified by the tuple (SHA256, community, [sandbox PROVIDER name],
    [start_date], [end_date], [status]).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for task in api.sandbox_task_list(sha256, sandbox=provider, start_date=start_date, end_date=end_date, status=status,
                                      account_id=account_id):
        output.sandbox_task(task)


@sandbox.command('my-tasks', short_help='Search for all the sandbox results created by my account or team.')
@click.option('--provider', 'sandbox_', type=click.STRING, help='Filter by slug of the sandbox provider.')
@click.option('--start-date', type=click.STRING, help='Tasks created the day passed or after (ISO format).')
@click.option('--end-date', type=click.STRING, help='Tasks created the day passed or before (ISO format).')
@click.option('--sha256', type=click.STRING, help='Only list tasks with the SHA256 passed.')
@click.pass_context
def my_task_list(ctx, sandbox_, start_date, end_date, sha256):
    """
    List the sandbox results associated with my account/team for the tuple (community, [sandbox], [start_date], [end_date])
    """
    api = ctx.obj['api']
    output = ctx.obj['output']

    for task in api.sandbox_my_tasks_list(sandbox=sandbox_, start_date=start_date, end_date=end_date, sha256=sha256):
        output.sandbox_task(task)
