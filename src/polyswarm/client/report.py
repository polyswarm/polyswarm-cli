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


@report.command('llm-create', short_help='Create an LLM report for an instance or sandbox id.')
@click.option('-i', '--instance-id', type=click.STRING, help='Instance ID to include in the report.')
@click.option('-s', '--sandbox-task-id', type=click.STRING, help='Sandbox Task ID to include in the report.')
@click.pass_context
def llm_create(ctx, instance_id, sandbox_task_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    if not instance_id and not sandbox_task_id:
         raise click.BadOptionUsage('instance_id', 'Either --instance-id or --sandbox-task-id must be provided.')

    result = api.llm_report_create(instance_id=instance_id, sandbox_task_id=sandbox_task_id)
    output.llm_report_task(result)


@report.command('llm-get', short_help='Fetch an LLM report task.')
@click.argument('report-id', callback=utils.validate_id)
@click.pass_context
def llm_get(ctx, report_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.llm_report_task(api.llm_report_get(report_task_id=report_id))


@report.command('llm-download', short_help='Download an LLM report.')
@click.argument('report-id', callback=utils.validate_id)
@click.option('-d', '--destination', type=click.Path(file_okay=False),
              help='Path where to store the downloaded file.', default=os.getcwd())
@click.pass_context
def llm_download(ctx, report_id, destination):
    api = ctx.obj['api']
    output = ctx.obj['output']
    report_object = api.llm_report_download(report_task_id=report_id, folder=destination)
    output.local_artifact(report_object)


@report.command('prompt-config-create', short_help='Create a new LLM prompt configuration.')
@click.argument('name', type=click.STRING)
@click.option('--system-prompt', required=True, type=click.STRING, help='The system prompt text.')
@click.option('--is-active', is_flag=True, default=False, help='Whether this should be the active prompt configuration.')
@click.option('--cape-only-prompt', type=click.STRING, help='Optional Cape-specific prompt text.')
@click.option('--triage-only-prompt', type=click.STRING, help='Optional Triage-specific prompt text.')
@click.option('--scan-only-prompt', type=click.STRING, help='Optional Scan-specific prompt text.')
@click.pass_context
def prompt_config_create(ctx, name, system_prompt, is_active, cape_only_prompt, triage_only_prompt, scan_only_prompt):
    api = ctx.obj['api']
    output = ctx.obj['output']
    
    result = api.prompt_config_create(
        name=name,
        system_prompt=system_prompt,
        is_active=is_active,
        cape_only_prompt=cape_only_prompt,
        triage_only_prompt=triage_only_prompt,
        scan_only_prompt=scan_only_prompt
    )
    output.llm_prompt_config(result)


@report.command('prompt-config-get', short_help='Fetch an LLM prompt configuration by ID.')
@click.argument('prompt-config-id', callback=utils.validate_id)
@click.pass_context
def prompt_config_get(ctx, prompt_config_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    
    result = api.prompt_config_get(prompt_config_id=prompt_config_id)
    output.llm_prompt_config(result)


@report.command('prompt-config-update', short_help='Update an existing LLM prompt configuration.')
@click.argument('prompt-config-id', callback=utils.validate_id)
@click.option('--name', type=click.STRING, help='The new name.')
@click.option('--system-prompt', type=click.STRING, help='The new system prompt text.')
@click.option('--is-active', type=bool, help='Whether this should be the active prompt configuration.')
@click.option('--cape-only-prompt', type=click.STRING, help='Optional Cape-specific prompt text.')
@click.option('--triage-only-prompt', type=click.STRING, help='Optional Triage-specific prompt text.')
@click.option('--scan-only-prompt', type=click.STRING, help='Optional Scan-specific prompt text.')
@click.pass_context
def prompt_config_update(ctx, prompt_config_id, name, system_prompt, is_active, cape_only_prompt, triage_only_prompt, scan_only_prompt):
    api = ctx.obj['api']
    output = ctx.obj['output']
    
    result = api.prompt_config_update(
        prompt_config_id=prompt_config_id,
        name=name,
        system_prompt=system_prompt,
        is_active=is_active,
        cape_only_prompt=cape_only_prompt,
        triage_only_prompt=triage_only_prompt,
        scan_only_prompt=scan_only_prompt
    )
    output.llm_prompt_config(result)


@report.command('prompt-config-list', short_help='List all LLM prompt configurations.')
@click.pass_context
def prompt_config_list(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    
    results = api.prompt_config_list()
    for result in results:
        output.llm_prompt_config(result)
