import click


@click.group(short_help='Interact with Metadata in Polyswarm.')
def metadata():
    pass


@metadata.command('rerun', short_help='Rerun metadata evaluation for the given hashes.')
@click.option('-a', '--analysis', type=click.STRING, multiple=True,
              help='Analysis to be execute on the Artifact.')
@click.option('-s', '--skip-es', type=click.BOOL, is_flag=True,
              help='Skip the upload to ES when evaluating the new metadata value.')
@click.argument('hashes', nargs=-1, required=True)
@click.pass_context
def create(ctx, analysis, skip_es, hashes):
    api = ctx.obj['api']
    output = ctx.obj['output']
    for artifact in api.rerun_metadata(hashes, analyses=analysis, skip_es=skip_es):
        output.artifact_instance(artifact)
