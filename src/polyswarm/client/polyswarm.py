from __future__ import absolute_import
import logging
try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import click
import click_log
import polyswarm_api
from click_log import core
from click.exceptions import Exit, ClickException
from polyswarm_api import exceptions as api_exceptions

import polyswarm
from polyswarm import exceptions
from polyswarm.polyswarm import Polyswarm
from polyswarm.formatters import formatters
from polyswarm.client.utils import validate_key
from polyswarm.client.hunt import live, historical
from polyswarm.client.scan import scan, lookup, wait, rescan, rescan_id
from polyswarm.client.download import download, cat, stream
from polyswarm.client.search import search
from polyswarm.client.rules import rules
from polyswarm.client.links import link
from polyswarm.client.tags import tag
from polyswarm.client.families import family
from polyswarm.client.metadata import metadata
from polyswarm.client.engine import engine

logger = logging.getLogger(__name__)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def setup_logging(verbosity):
    # explicitly set to stderr just in case
    # this is the new default for click_log it seems
    core.ClickHandler._use_stderr = True
    # adding color to INFO log messages as well
    core.ColorFormatter.colors['info'] = dict(fg='green')

    class NamedColorFormatter(core.ColorFormatter):
        def format(self, record):
            if not record.exc_info:
                level = record.levelname.lower()
                msg = record.getMessage()
                if level in self.colors:
                    prefix = click.style('{} [{}]: '.format(level, record.name),
                                         **self.colors[level])
                    msg = '\n'.join(prefix + x for x in msg.splitlines())
                return msg
            return logging.Formatter.format(self, record)

    # replace the formatter with our formatter so that it prints the logger name
    core._default_handler.formatter = NamedColorFormatter()

    if verbosity >= 3:
        log_level = logging.DEBUG
        # set the root logger and any other internal loggers to debug as well if -vvv is provided
        click_log.basic_config().setLevel(log_level)
    elif verbosity == 2:
        log_level = logging.DEBUG
    elif verbosity == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    click_log.basic_config('polyswarm').setLevel(log_level)
    click_log.basic_config('polyswarm_api').setLevel(log_level)


class ExceptionHandlingGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super(ExceptionHandlingGroup, self).invoke(ctx)
        except (
                exceptions.NoResultsException,
                exceptions.NotFoundException,
                api_exceptions.NoResultsException,
                api_exceptions.NotFoundException,
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
@click.option('-a', '--api-key', help='Your API key for polyswarm.network (required).',
              default='', callback=validate_key, envvar='POLYSWARM_API_KEY')
@click.option('-u', '--api-uri', default='https://api.polyswarm.network/v2',
              envvar='POLYSWARM_API_URI', help='The API endpoint (ADVANCED).')
@click.option('-o', '--output-file', type=click.File('w', encoding='utf8'), help='Path to output file.')
@click.option('--output-format', '--fmt', default='text', type=click.Choice(formatters.keys()),
              help='Output format. Human-readable text or JSON.')
@click.option('--color/--no-color', default=True, help='Use colored output in text mode.')
@click.option('-v', '--verbose', default=0, count=True)
@click.option('-c', '--community', default='default', envvar='POLYSWARM_COMMUNITY', help='Community to use.')
@click.option('--parallel', default=8, help='Number of threads to be used in parallel http requests.')
@click.version_option(polyswarm.__version__, '--version', prog_name='polyswarm-cli')
@click.version_option(polyswarm_api.__version__, '--api-version', prog_name='polyswarm-api')
@click.pass_context
def polyswarm_cli(ctx, api_key, api_uri, output_file, output_format, color, verbose, community, parallel):
    """
    This is a PolySwarm CLI client, which allows you to interact directly
    with the PolySwarm network to scan files, search hashes, and more.
    """
    setup_logging(verbose)
    logger.info('Running polyswarm-cli version %s with polyswarm-api version %s',
                polyswarm.__version__, polyswarm_api.__version__)

    ctx.obj = {}

    if ctx.invoked_subcommand is None:
        return

    output_file = output_file or click.get_text_stream('stdout')

    ctx.obj['api'] = Polyswarm(api_key, uri=api_uri, community=community, parallel=parallel)
    ctx.obj['output'] = formatters[output_format](color=color, output=output_file)


commands = [
    scan, wait, lookup, search, live, historical,
    download, cat, stream, rescan, rescan_id,
    rules, link, tag, family, metadata,
    engine,
]

for command in commands:
    polyswarm_cli.add_command(command)
