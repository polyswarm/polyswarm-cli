import logging
import os

import click


from polyswarm.client import utils

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with the Polyswarm reporting system.')
def report():
    pass


SECTIONS = "summary, detections, fileMetadata, network, droppedFiles, extractedConfig, analysis"


@report.command('create', short_help='Create a report for an instance or sandbox id.')
@click.argument('format', type=click.Choice(['html', 'pdf']))
@click.argument('type', type=click.Choice(['scan', 'sandbox']))
@click.argument('object-id', callback=utils.validate_id)
@click.option('--template-id', metavar='ID', type=click.STRING)
@click.option('--includes',
              help=f'Comma-separated list of sections to include in the report. Can be one ore more of: {SECTIONS}',
              multiple=True,
              callback=lambda _,o,x: x[0].split(',') if len(x) == 1 else x)
@click.option('--excludes',
              help=f'Comma-separated list of sections to exclude in the report. Can be one ore more of: {SECTIONS}',
              multiple=True,
              callback=lambda _,o,x: x[0].split(',') if len(x) == 1 else x)
@click.pass_context
def create(ctx, format, type, object_id, template_id, includes, excludes):
    api = ctx.obj['api']
    output = ctx.obj['output']
    object_d = {'instance_id': object_id} if type == 'scan' else {'sandbox_task_id': object_id}
    template_metadata = {}
    if includes:
        template_metadata['includes'] = includes
    if excludes:
        template_metadata['excludes'] = excludes
    output.report_task(api.report_create(type=type,
                                         format=format,
                                         template_id=template_id,
                                         template_metadata=template_metadata or None,
                                         **object_d))


@report.command('get', short_help='Fetch a report task for an instance or sandbox id.')
@click.argument('report-id', callback=utils.validate_id)
@click.pass_context
def file(ctx, report_id):
    api = ctx.obj['api']
    output = ctx.obj['output']

    output.report_task(api.report_get(id=report_id))


@report.command('download', short_help='Download a report for an instance or sandbox id.')
@click.argument('report-id', callback=utils.validate_id)
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded file.', default=os.getcwd())
@click.pass_context
def download(ctx, report_id, destination):
    api = ctx.obj['api']
    out = ctx.obj['output']

    report_object = api.report_download(report_id, destination)
    out.local_artifact(report_object)
