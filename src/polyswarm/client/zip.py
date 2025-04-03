import logging
import os

import click

from polyswarm.client import utils
from polyswarm_api import settings, resources

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with creating or downloading a password protected Zip archive of sample/s.')
def zip():
    pass


@zip.command('create', short_help='Create a zip for an instance/s.')
@click.option('-i', '--instance_id', type=click.STRING, multiple=True,
              help='The ID of an instance to include in the zip archive.')
@click.pass_context
def create(ctx, instance_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    task = api.sample_zip_task_create(instance_id)
    output.sample_zip_task(task)


@zip.command('get', short_help='Fetch a zip task for an instance or sandbox id.')
@click.argument('zip-task-id', callback=utils.validate_id)
@click.pass_context
def get(ctx, zip_task_id):
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.sample_zip_task(api.sample_zip_task_get(id=zip_task_id))


@zip.command('download', short_help='Download a zip archive from a completed zip task.')
@click.argument('zip-task-id', callback=utils.validate_id)
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded file.', default=os.getcwd())
@click.pass_context
def download(ctx, zip_task_id, destination):
    api = ctx.obj['api']
    out = ctx.obj['output']

    zip_object = api.sample_zip_download(zip_task_id, destination)
    out.local_artifact(zip_object)

