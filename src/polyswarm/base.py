import click
import logging
import sys

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

from polyswarm_api import exceptions as api_exceptions
from polyswarm_api.api import PolyswarmAPI
from polyswarm.formatters import formatters
from polyswarm_api import get_version as get_polyswarm_api_version

from polyswarm import exceptions
from .utils import validate_key
from .hunt import live, historical
from .scan import scan, url_scan, rescan, lookup
from .download import download, cat, stream
from .search import search

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
VERSION = '2.0.0.dev4'


class ExceptionHandlingGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super(ExceptionHandlingGroup, self).invoke(ctx)
        except exceptions.NoResultsException as e:
            click.secho(str(e), fg='red')
            sys.exit(1)
        except api_exceptions.NotFoundException as e:
            click.secho(str(e), fg='red')
            sys.exit(1)
        except api_exceptions.InvalidYaraRulesException as e:
            output = ctx.obj.get('output')
            if output:
                output.invalid_rule(e)
            sys.exit(2)
        except api_exceptions.UsageLimitsExceededException as e:
            output = ctx.obj.get('output')
            if output:
                output.usage_exceeded()
            sys.exit(2)
        except api_exceptions.PolyswarmException as e:
            click.secho(str(e), fg='red')
            sys.exit(2)
        except JSONDecodeError:
            sys.exit(2)
        except UnicodeDecodeError:
            sys.exit(2)


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
    ctx.obj = {}

    if ctx.invoked_subcommand is None:
        return

    if verbose > 2:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARN

    logging.basicConfig(level=log_level)

    # only allow color for stdout
    if output_file is not None:
        color = False
    else:
        output_file = click.get_text_stream('stdout')

    logging.debug('Creating API instance: api_key: %s, api_uri: %s', api_key, api_uri)
    ctx.obj['api'] = PolyswarmAPI(api_key, api_uri, community=community, validate_schemas=validate)
    ctx.obj['output'] = formatters[output_format](color=color, output=output_file)
    ctx.obj['parallel'] = parallel


commands = [scan, url_scan, rescan, lookup, search, live, historical, download, cat, stream]

for command in commands:
    polyswarm.add_command(command)
