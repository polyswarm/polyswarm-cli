import logging
import sys
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import click
import click_log
from click.exceptions import Exit, ClickException
from polyswarm_api import exceptions as api_exceptions
from polyswarm_api.api import PolyswarmAPI
from polyswarm.formatters import formatters
from polyswarm_api import get_version as get_polyswarm_api_version

from polyswarm import exceptions
from .utils import validate_key
from .hunt import live, historical
from .scan import scan, lookup, wait
from .download import download, cat, stream
from .search import search

logger = logging.getLogger(__name__)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VERSION = '2.0.0.dev6'


class ExceptionHandlingGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super(ExceptionHandlingGroup, self).invoke(ctx)
        except (
                exceptions.NoResultsException,
                exceptions.NotFoundException,
        ) as e:
            logger.error(e)
            raise Exit(1)
        except (
                exceptions.PartialResultsException,
        ) as e:
            logger.error(e)
            raise Exit(3)
        except (
                exceptions.InternalFailureException,
                api_exceptions.PolyswarmException,
                exceptions.PolyswarmException,
                JSONDecodeError,
                UnicodeDecodeError,
        ) as e:
            logger.error(e)
            raise Exit(2)
        except (Exit, ClickException):
            raise
        except Exception as e:
            logger.exception(e)
            logger.error('Unhandled exception happened. Please contact support.')
            raise Exit(2)


@click.group(cls=ExceptionHandlingGroup, context_settings=CONTEXT_SETTINGS)
@click.option('-a', '--api-key', help='Your API key for polyswarm.network (required)',
              default='', callback=validate_key, envvar='POLYSWARM_API_KEY')
@click.option('-u', '--api-uri', default='https://api.polyswarm.network/v2',
              envvar='POLYSWARM_API_URI', help='The API endpoint (ADVANCED)')
@click.option('-o', '--output-file', type=click.File('w'), help='Path to output file.')
@click.option('--output-format', '--fmt', default='text', type=click.Choice(formatters.keys()),
              help='Output format. Human-readable text or JSON.')
@click.option('--color/--no-color', default=True, help='Use colored output in text mode.')
@click.option('-v', '--verbose', default=0, count=True)
@click.option('-c', '--community', default='lima', envvar='POLYSWARM_COMMUNITY', help='Community to use.')
@click.option('--advanced-disable-version-check/--advanced-enable-version-check', default=False,
              help='Enable/disable GitHub release version check.')
@click.option('--validate', default=False, is_flag=True,
              envvar='POLYSWARM_VALIDATE', help='Validate incoming schemas (note: slow).')
@click.option('--parallel', default=8, help='Number of threads to be used in parallel http requests.')
@click.version_option(VERSION, '--version', prog_name='polyswarm-cli')
@click.version_option(get_polyswarm_api_version(), '--api-version', prog_name='polyswarm-api')
@click.pass_context
def polyswarm(ctx, api_key, api_uri, output_file, output_format, color, verbose, community,
              advanced_disable_version_check, validate, parallel):
    """
    This is a PolySwarm CLI client, which allows you to interact directly
    with the PolySwarm network to scan files, search hashes, and more.
    """
    if verbose >= 2:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    click_log.basic_config('polyswarm').setLevel(log_level)
    click_log.basic_config('polyswarm_api').setLevel(log_level)

    logger.info('Running polyswarm-cli version %s with polyswarm-api version %s', VERSION, get_polyswarm_api_version())

    ctx.obj = {}

    if ctx.invoked_subcommand is None:
        return

    # only allow color for stdout
    if output_file is not None:
        color = False
    else:
        output_file = click.get_text_stream('stdout')

    ctx.obj['api'] = PolyswarmAPI(api_key, api_uri, community=community, validate_schemas=validate)
    ctx.obj['output'] = formatters[output_format](color=color, output=output_file)
    ctx.obj['parallel'] = parallel


commands = [scan, wait, lookup, search, live, historical, download, cat, stream]

for command in commands:
    polyswarm.add_command(command)
