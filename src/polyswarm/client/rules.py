import click

from polyswarm_api import exceptions as api_exceptions

from polyswarm import exceptions
from polyswarm.client import utils


@click.group(short_help='Interact with Yara Rules stored in Polyswarm.')
def rules():
    pass


@rules.command('create', short_help='Create a ruleset.')
@click.argument('rule_name', type=str)
@click.argument('rule_file', type=click.File('r'), required=True)
@click.option('-d', '--description', type=str, help='Description of the ruleset.')
@click.pass_context
def create(ctx, rule_name, rule_file, description):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.ruleset(api.ruleset_create(rule_name, rule_file.read(), description=description))


@rules.command('delete', short_help='Delete a ruleset.')
@click.argument('rule_id', type=click.INT, required=True)
@click.pass_context
def delete(ctx, rule_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.ruleset(api.ruleset_delete(rule_id))


@rules.command('list', short_help='List rulesets, optionally filtered.')
@click.option('-n', '--name', help='Substring match on the ruleset name (case-insensitive).')
@click.option('-s', '--status', type=click.Choice(['active']),
              help='Only rulesets whose live hunt is currently running.')
@click.option('--favorites-only', is_flag=True, help='Only favorited (starred) rulesets.')
@click.option('--has-new-results', is_flag=True,
              help='Only rulesets whose stored new-results counter is positive.')
@click.pass_context
def list_rules(ctx, name, status, favorites_only, has_new_results):
    """List rulesets, optionally filtered. All filters are conjunctive.

    Filtering is applied SERVER-side: the list is keyset-paginated, so a
    client filtering locally would have to walk every page to find matches.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    # A False flag is not a filter: send only what the caller actually asked for.
    kwargs = {k: v for k, v in (('name', name), ('status', status),
                                ('favorites_only', favorites_only or None),
                                ('has_new_results', has_new_results or None))
              if v is not None}
    for ruleset in api.ruleset_list(**kwargs):
        output.ruleset(ruleset)


@rules.command('favorite', short_help='Favorite (star) or unfavorite a ruleset.')
@click.argument('rule_id', type=click.INT, required=True)
@click.option('--unfavorite', is_flag=True, help='Remove the star instead.')
@click.pass_context
def favorite(ctx, rule_id, unfavorite):
    """Star a ruleset for the whole team (or unstar with --unfavorite).

    Stars are shared by the team and capped server-side; the response renders
    the new state plus the budget ("N of M favorites used"). When the budget
    is full the server refuses with a machine-readable FAVORITE_LIMIT error,
    rendered here as a clean message rather than a traceback (exit 2, not 1 —
    1 is reserved for no-results/not-found).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    try:
        output.ruleset_favorite(api.ruleset_favorite(rule_id, favorite=not unfavorite))
    except api_exceptions.RequestException as exc:
        # `exc.request` needs no guard: __init__ always assigns it, and a None
        # request flows safely through the getattr.
        errors = getattr(exc.request, 'errors', None) or {}
        if isinstance(errors, dict) and errors.get('code') == 'FAVORITE_LIMIT':
            used = errors.get('favorites_used')
            limit = errors.get('favorites_limit')
            # Counters are advisory; fall back rather than render "(None of None)".
            # `.json` is the response envelope and `result` a key inside it —
            # the request has no `.result`, only a private `._result`. getattr
            # so a bare request still reaches the message (specs/05).
            envelope = getattr(exc.request, 'json', None)
            server_msg = envelope.get('result') if isinstance(envelope, dict) else None
            budget = (f'Favorite limit reached ({used} of {limit} used).'
                      if used is not None and limit is not None
                      else (server_msg if isinstance(server_msg, str)
                            else 'Favorite limit reached.'))
            # PolyswarmException exits 2; ClickException would exit 1, reserved
            # for no-results/not-found.
            # Only starring can hit the cap, and only it has a remedy.
            remedy = ('' if unfavorite else
                      ' Unfavorite another ruleset first: '
                      '`polyswarm rules favorite <id> --unfavorite`.')
            raise exceptions.PolyswarmException(f'{budget}{remedy}') from exc
        raise


@rules.command('update', short_help='Update a ruleset.')
@click.argument('rule_id', type=click.INT, required=True)
@click.option('-n', '--name', type=str, help='Name of the ruleset.')
@click.option('-f', '--file', type=click.File('r'), help='File containing the Yara rules.')
@click.option('-d', '--description', type=str, help='Description of the ruleset.')
@click.pass_context
@utils.any_provided('name', 'file', 'description')
def update(ctx, rule_id, name, file, description):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.ruleset(api.ruleset_update(
        rule_id,
        name=name if name else None,
        rules=file.read() if file else None,
        description=description if description else None,
    ))


@rules.command('view', short_help='View a ruleset.')
@click.argument('rule_id', type=click.INT, required=True)
@click.pass_context
def view(ctx, rule_id):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.ruleset(api.ruleset_get(rule_id), contents=True)


