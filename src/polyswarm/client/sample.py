import logging

import click


logger = logging.getLogger(__name__)


@click.command('sample', short_help='Get aggregated sample information.')
@click.argument('sha256', required=True)
@click.option('--artifact-instance-id', type=int, default=None,
              help='Specific artifact instance ID to retrieve.')
@click.option('--sandbox-task-id-cape', type=int, default=None,
              help='Specific Cape sandbox task ID to retrieve.')
@click.option('--sandbox-task-id-triage', type=int, default=None,
              help='Specific Triage sandbox task ID to retrieve.')
@click.option('--artifact-metadata-id', type=int, default=None,
              help='Specific artifact metadata ID to retrieve.')
@click.option('--llm-report-id', type=int, default=None,
              help='Specific LLM report task ID to retrieve.')
@click.pass_context
def sample(ctx, sha256, artifact_instance_id, sandbox_task_id_cape,
           sandbox_task_id_triage, artifact_metadata_id, llm_report_id):
    """
    Get aggregated sample information including artifact instance, sandbox tasks, metadata,
    and LLM report.

    SHA256 is the SHA256 hash of the artifact to retrieve information for.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    result = api.sample(
        sha256,
        artifact_instance_id=artifact_instance_id,
        sandbox_task_id_cape=sandbox_task_id_cape,
        sandbox_task_id_triage=sandbox_task_id_triage,
        artifact_metadata_id=artifact_metadata_id,
        llm_report_id=llm_report_id,
    )
    output.sample(result)
