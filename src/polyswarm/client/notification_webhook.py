import logging

import click

from polyswarm.client import utils

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with Notification Webhooks in Polyswarm.')
def webhook():
    pass


@webhook.command('create', short_help='Create a new webhook.')
@click.argument('webhook-uri', type=click.STRING, required=True)
@click.argument('secret', type=click.STRING, required=True)
@click.option('--status', type=click.Choice(['enabled', 'disabled']), default='enabled',
              help='Webhook status (default: enabled).')
@click.option('--events', type=click.STRING, multiple=True, 
              help='Event types to subscribe to (can be specified multiple times).')
@click.pass_context
def create(ctx, webhook_uri, secret, status, events):
    """
    Create a new webhook.
    
    WEBHOOK_URI: The URI where notification webhook events should be sent
    SECRET: The secret key used for HMAC signature verification
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    
    result = api.webhook_create(webhook_uri=webhook_uri, secret=secret, status=status, events=events)
    output.webhook(result)


@webhook.command('get', short_help='Get a webhook by ID.')
@click.argument('webhook-id', callback=utils.validate_id)
@click.pass_context
def get(ctx, webhook_id):
    """
    Get a notification webhook by ID.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    output.webhook(api.webhook_get(webhook_id))


@webhook.command('update', short_help='Update an existing webhook.')
@click.argument('webhook-id', callback=utils.validate_id)
@click.option('--webhook-uri', type=click.STRING, help='The new webhook URI.')
@click.option('--secret', type=click.STRING, help='The new secret for HMAC signing.')
@click.option('--status', type=click.Choice(['enabled', 'disabled']), help='The new status.')
@click.option('--events', type=click.STRING, multiple=True,
              help='Event types to subscribe to (can be specified multiple times).')
@click.pass_context
@utils.any_provided('webhook_uri', 'secret', 'status', 'events')
def update(ctx, webhook_id, webhook_uri, secret, status, events):
    """
    Update an existing notification webhook.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    
    result = api.webhook_update(
        webhook_id=webhook_id,
        webhook_uri=webhook_uri,
        secret=secret,
        status=status,
        events=events
    )
    output.webhook(result)


@webhook.command('delete', short_help='Delete a webhook.')
@click.argument('webhook-id', callback=utils.validate_id)
@click.pass_context
def delete(ctx, webhook_id):
    """
    Delete a notification webhook.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    api.webhook_delete(webhook_id)
    click.echo(f'Webhook {webhook_id} deleted successfully')


@webhook.command('list', short_help='List all webhooks.')
@click.pass_context
def list_webhooks(ctx):
    """
    List all notification webhooks for the current account.
    """
    api = ctx.obj['api']
    output = ctx.obj['output']
    for webhook_obj in api.webhook_list():
        output.webhook(webhook_obj)


@webhook.command('test', short_help='Test a webhook by sending a test payload.')
@click.argument('webhook-id', callback=utils.validate_id)
@click.pass_context
def test(ctx, webhook_id):
    """
    Test a notification webhook by sending a test payload.
    """
    api = ctx.obj['api']
    api.webhook_test(webhook_id)
    click.echo(f'Test payload sent to webhook {webhook_id}')
