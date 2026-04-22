import logging

import click


logger = logging.getLogger(__name__)


@click.group('sample', short_help='Interact with sample information.')
def sample():
    pass


@sample.command('get', short_help='Get aggregated sample information.')
@click.argument('sha256', required=True)
@click.option('--artifact-instance-id', type=int, default=None,
              help='Specific artifact instance ID to retrieve.')
@click.option('--sandbox-task-id-cape', type=int, default=None,
              help='Specific Cape sandbox task ID to retrieve.')
@click.option('--sandbox-task-id-triage', type=int, default=None,
              help='Specific Triage sandbox task ID to retrieve.')
@click.option('--artifact-metadata-id', type=int, default=None,
              help='Specific artifact metadata ID to retrieve.')
@click.pass_context
def sample_get(
    ctx, sha256, artifact_instance_id, sandbox_task_id_cape, sandbox_task_id_triage, artifact_metadata_id
):
    """
    Get aggregated sample information including artifact instance, sandbox tasks, and metadata.

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
    )
    output.sample(result)


@sample.command('submit-url', short_help='Submit a URL or IP for IP analysis.')
@click.argument('url', nargs=-1, type=click.STRING, required=True)
@click.pass_context
def sample_submit_url(ctx, url):
    """
    Submit a URL or IP for IP analysis. Does not trigger scanning.

    Creates an ArtifactInstance immediately (no S3 upload), triggers only
    the IP analyzer, and consumes no quota.

    URL is the URL or IP address to submit for analysis.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    for u in url:
        instance = api.submit_url(u)
        output.artifact_instance(instance)
