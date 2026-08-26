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


@rules.command('list', short_help='List all rulesets.')
@click.pass_context
def list_rules(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    # Zero-argument on purpose: every hunt-page field this renders (counts,
    # favorites, tracking) arrives as a plain response field the formatters
    # getattr-guard, so the command needs NO new SDK behaviour and works
    # unchanged on the pin's floor (4.3.0). The new-results badge is a STORED
    # server-side counter refreshed on a schedule — there is no per-request
    # count to ask for.
    for ruleset in api.ruleset_list():
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
    rendered here as a clean message rather than a traceback (still exit 2 —
    the central mapping's server-refusal code; exit 1 means no-results).
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    toggle = getattr(api, 'ruleset_favorite', None)
    if toggle is None:
        # The declared floor (published polyswarm-api 4.3.0) predates the
        # favorite surface — it ships in the paired SDK change. Every OTHER
        # command keeps working on the floor (list is zero-argument again);
        # only this command needs the newer SDK, and on the floor it must
        # fail with a clean upgrade message, never an AttributeError
        # traceback. (Same principle as the withdrawn --include-counts flag:
        # a new surface may require the new SDK; existing surfaces may not.)
        raise exceptions.PolyswarmException(
            'rules favorite requires a polyswarm-api release newer than '
            '4.3.0 (the paired SDK change adds ruleset_favorite). '
            'Upgrade polyswarm-api to use this command.')
    try:
        output.ruleset_favorite(toggle(rule_id, not unfavorite))
    except api_exceptions.RequestException as exc:
        errors = getattr(exc.request, 'errors', None) or {}
        if isinstance(errors, dict) and errors.get('code') == 'FAVORITE_LIMIT':
            # The one refusal a user fixes themselves (unstar something):
            # say so cleanly. A CLI PolyswarmException keeps the central
            # exit-code mapping's 2 (server refusal) — a ClickException
            # would exit 1, the code reserved for no-results/not-found.
            raise exceptions.PolyswarmException(
                f"Favorite limit reached ({errors.get('favorites_used')} of "
                f"{errors.get('favorites_limit')} used). Unfavorite another "
                f'ruleset first: `polyswarm rules favorite <id> --unfavorite`.'
            ) from exc
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


