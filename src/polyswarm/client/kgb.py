import json

import click


@click.group('kgb', short_help='Manage Known Good Binaries (internal-only).')
def kgb():
    """Create, retrieve, and delete Known Good Binaries (KGB) entries.

    A known-good entry is keyed on its sha256. Creating one records a feed as
    having flagged the hash as good; retrieving and deleting are both keyed on
    the same sha256. There is no update. Access is gated server-side to
    internal accounts.
    """
    pass


@kgb.command('create', short_help='Record a sha256 as a known-good binary.')
@click.argument('source', type=click.STRING, required=True)
@click.argument('sha256', type=click.STRING, required=True)
@click.option('--sha1', type=click.STRING, default=None, help='Optional sha1.')
@click.option('--md5', type=click.STRING, default=None, help='Optional md5.')
@click.option('--filename', type=click.STRING, default=None, help='Optional filename.')
@click.option('--mimetype', type=click.STRING, default=None, help='Optional mimetype.')
@click.option('--metadata', type=click.STRING, default=None,
              help='Optional extra feed metadata as JSON (the server enforces the shape).')
@click.pass_context
def create(ctx, sha256, source, sha1, md5, filename, mimetype, metadata):
    """Record SHA256 as a known-good binary, flagged by SOURCE."""
    api = ctx.obj['api']
    output = ctx.obj['output']
    if metadata is not None:
        # Parse into JSON so it's sent as structured data; the server validates
        # the value (e.g. that it's an object) so the rule stays consistent
        # across every client.
        try:
            metadata = json.loads(metadata)
        except ValueError as e:
            raise click.BadParameter(f'must be valid JSON: {e}', param_hint='--metadata')
    output.known_good(api.known_good_create(
        sha256,
        source=source,
        sha1=sha1,
        md5=md5,
        filename=filename,
        mimetype=mimetype,
        metadata=metadata,
    ))


@kgb.command('get', short_help='Retrieve a known-good entry by sha256.')
@click.argument('sha256', type=click.STRING, required=True)
@click.pass_context
def get(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.known_good(api.known_good_get(sha256))


@kgb.command('delete', short_help='Delete a known-good entry by sha256.')
@click.argument('sha256', type=click.STRING, required=True)
@click.pass_context
def delete(ctx, sha256):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.known_good(api.known_good_delete(sha256))
