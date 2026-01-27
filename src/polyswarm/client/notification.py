import logging

import click

from polyswarm.client.notification_webhook import webhook

logger = logging.getLogger(__name__)


@click.group(short_help='Interact with Polyswarm notification systems.')
def notification():
    pass


# Add webhook as a subcommand of notification
notification.add_command(webhook)
