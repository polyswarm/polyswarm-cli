from __future__ import absolute_import
import click

from polyswarm.client import utils


@click.group(short_help='Interact with Metadata in Polyswarm.')
def metadata():
    pass


@metadata.command('rerun', short_help='Rerun metadata evaluation for the given hashes.')
@click.option('-r', '--hash-file', help='File of hashes, one per line.', type=click.File('r'))
@click.option('-a', '--analysis', type=click.STRING, multiple=True,
              help='Analysis to be execute on the Artifact.')
@click.option('-s', '--skip-es', type=click.BOOL, is_flag=True,
              help='Skip the upload to ES when evaluating the new metadata value.')
@click.argument('hashes', nargs=-1)
@click.pass_context
@utils.any_provided('hashes', 'hash_file')
def rerun(ctx, hash_file, analysis, skip_es, hashes):
    api = ctx.obj['api']
    output = ctx.obj['output']
    if not (hash_file or hashes):
        raise click.exceptions.BadArgumentUsage('One of HASHES or --hash-file should be provided.')
    hashes = utils.parse_hashes(hashes, hash_file=hash_file)
    for artifact in api.rerun_metadata(hashes, analyses=analysis, skip_es=skip_es):
        output.artifact_instance(artifact)
