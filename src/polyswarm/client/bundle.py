import logging
import os

import click

from polyswarm.client import utils
from polyswarm_api import settings, resources

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with creating or downloading a password protected bundle archive of sample/s.')
def bundle():
    pass


@bundle.command('create', short_help='Create a bundle for an instance/s.')
@click.option('-i', '--instance-id', type=click.STRING, multiple=True,
              help='The ID of an instance to include in the bundle archive.')
@click.option('-n', '--archive-name', type=click.STRING, help='Name of the archive that will be created.')
@click.option('-p', '--preserve-filenames', type=click.BOOL, is_flag=True, default=False,
              help='Preserve the names of the files in the bundle.')
@click.pass_context
def create(ctx, instance_id, archive_name, preserve_filenames):
    api = ctx.obj['api']
    output = ctx.obj['output']
    task = api.sample_bundle_task_create(instance_id, filename=archive_name, preserve_filenames=preserve_filenames)
    output.bundle_task(task)


@bundle.command('get', short_help='Fetch a bundle task for an instance or sandbox id.')
@click.argument('bundle-task-id', callback=utils.validate_id)
@click.pass_context
def get(ctx, bundle_task_id):
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.bundle_task(api.sample_bundle_task_get(id=bundle_task_id))


@bundle.command('download', short_help='Download a bundle archive from a completed bundle task.')
@click.argument('bundle-task-id', callback=utils.validate_id)
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded file.', default=os.getcwd())
@click.pass_context
def download(ctx, bundle_task_id, destination):
    api = ctx.obj['api']
    out = ctx.obj['output']

    bundle_object = api.sample_bundle_download(bundle_task_id, destination)
    out.local_artifact(bundle_object)

