import logging
import os

import click

from polyswarm.client import utils
from polyswarm_api import settings, resources

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with the Polyswarm reporting system.')
def report():
    pass


SECTIONS = "summary, detections, fileMetadata, network, droppedFiles, extractedConfig, analysis"
SANDBOX_ARTIFACT_TYPES = "report, raw_report, screenshot, recording, dropped_file, memory_dump, pcap, jarm"


@report.command('create', short_help='Create a report for an instance or sandbox id.')
@click.argument('format', type=click.Choice(['html', 'pdf', 'zip']))
@click.argument('type', type=click.Choice(['scan', 'sandbox']))
@click.argument('object-id', callback=utils.validate_id)
@click.option('--template-id', metavar='ID', type=click.STRING)
@click.option('--includes',
              help=f'Comma-separated list of sections to include in the report. Can be one ore more of: {SECTIONS}',
              multiple=True,
              callback=lambda _,o,x: x[0].split(',') if len(x) == 1 else x)
@click.option('--sandbox_artifact_types',
              help=f'Comma-separated list of sandbox artifact types to include in the zip.\
                     Can be one ore more of: {SANDBOX_ARTIFACT_TYPES}.  Only applicable to sandbox_zip type.',
              multiple=True,
              callback=lambda _, o, x: x[0].split(',') if len(x) == 1 else x)
@click.option('--zip-report-ids',
              help=f'Comma-separated list of report task ids to include in the zip.',
              multiple=True,
              callback=lambda _, o, x: x[0].split(',') if len(x) == 1 else x)
@click.option('-n', '--nowait', is_flag=True,
              help='Does not wait for the report generation to finish, just create it and return right away.')
@click.option('-t', '--timeout', type=click.INT, default=settings.DEFAULT_REPORT_TIMEOUT,
              help=f'How long to wait for results.', show_default=True)
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded report.', default=os.getcwd())
@click.pass_context
def create(ctx, format, type, object_id, template_id, includes, sandbox_artifact_types, zip_report_ids, nowait, timeout, destination):
    api = ctx.obj['api']
    output = ctx.obj['output']
    object_d = {'instance_id': object_id} if type == 'scan' else {'sandbox_task_id': object_id}
    template_metadata = {}
    if includes:
        template_metadata['includes'] = includes
    if sandbox_artifact_types:
        template_metadata['sandbox_artifact_types'] = sandbox_artifact_types
    if format == 'zip':
        type = 'sandbox_zip'
        if zip_report_ids:
            template_metadata['zip_report_ids'] = zip_report_ids
    result = api.report_create(type=type,
                               format=format,
                               template_id=template_id,
                               template_metadata=template_metadata or None,
                               **object_d)
    if nowait:
        output.report_task(result)
    else:
        _report = api.report_wait_for(result.id, timeout)
        if destination:
            result = _report.download_report(folder=destination).result()
            result.handle.close()
            output.local_artifact(result)


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
