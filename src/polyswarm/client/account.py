import logging

import click

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with Accounts in Polyswarm.')
def account():
    pass


@account.command('whois', short_help='Fetch basic information about the account.')
@click.pass_context
def whois(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.account_whois(api.account_whois())


@account.command('features', short_help='Fetch account features and quota.')
@click.pass_context
def whois(ctx):
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.account_features(api.account_features())
