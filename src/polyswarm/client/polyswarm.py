import logging
from json import JSONDecodeError

import click
import click_log
import polyswarm_api
from click_log import core
from click.exceptions import Exit, ClickException
from click.core import ParameterSource
from polyswarm_api import exceptions as api_exceptions

import polyswarm
from polyswarm import exceptions
from polyswarm.polyswarm import Polyswarm
from polyswarm.formatters import formatters
from polyswarm.client.utils import validate_key
from polyswarm.client.live import live
from polyswarm.client.historical import historical
from polyswarm.client.scan import scan, lookup, wait, rescan, rescan_id
from polyswarm.client.sandbox import sandbox, sandbox_list
from polyswarm.client.download import download, cat, stream, download_id, download_sandbox_artifact
from polyswarm.client.search import known, search
from polyswarm.client.rules import rules
from polyswarm.client.links import link
from polyswarm.client.tags import tag
from polyswarm.client.families import family
from polyswarm.client.metadata import metadata
from polyswarm.client.engine import engine
from polyswarm.client.event import activity
from polyswarm.client.report import report
from polyswarm.client.bundle import bundle
from polyswarm.client.report_template import report_template
from polyswarm.client.account import account
from polyswarm.client.notification import notification
from polyswarm.client.sample import sample
from polyswarm.client.kgb import kgb

logger = logging.getLogger(__name__)

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# Default production endpoint, used when neither --api-uri nor an environment
# shortcut is given.
PROD_API_URI = 'https://api.polyswarm.network/v3'

# Convenience environment shortcuts so callers can write `--stage` instead of
# `--api-uri https://api.stage-blue.polyswarm.network/v3`. Keys are the click
# parameter names (click maps `--prod-eu` -> `prod_eu`).
API_URI_SHORTCUTS = {
    'prod': PROD_API_URI,
    'stage': 'https://api.stage-blue.polyswarm.network/v3',
    'local': 'http://localhost:9696/v3',
    'prod_eu': 'https://api.prod-eu-v3.polyswarm.network/v3',
    'stage_eu': 'https://api.stage-eu-blue.polyswarm.network/v3',
}

_SHORTCUT_FLAGS = {
    'prod': '--prod', 'stage': '--stage', 'local': '--local',
    'prod_eu': '--prod-eu', 'stage_eu': '--stage-eu',
}


def resolve_api_uri(api_uri, api_uri_from_cli, shortcuts):
    """Resolve the effective API endpoint, honouring the precedence:

        explicit command-line flag  >  POLYSWARM_API_URI env var  >  production

    ``api_uri`` is the value click resolved for --api-uri (from the command
    line, the ``POLYSWARM_API_URI`` env var, or ``None`` when neither was
    given). ``api_uri_from_cli`` is True only when --api-uri was passed
    explicitly on the command line (parameter source ``COMMANDLINE``), not via
    the env var. ``shortcuts`` maps each shortcut parameter name to whether its
    flag was set.

    The shortcuts are mutually exclusive with each other and with an explicit
    command-line --api-uri. An ambient ``POLYSWARM_API_URI`` does **not**
    conflict with a shortcut — the explicit flag wins. With no shortcut, an
    explicit --api-uri or the env var is used; with nothing at all, default to
    production.
    """
    selected = [name for name, enabled in shortcuts.items() if enabled]
    if len(selected) > 1:
        flags = ', '.join(_SHORTCUT_FLAGS[name] for name in selected)
        raise click.UsageError(f'Environment shortcuts are mutually exclusive; got {flags}.')
    if selected and api_uri_from_cli:
        raise click.UsageError(
            f'{_SHORTCUT_FLAGS[selected[0]]} cannot be combined with an explicit --api-uri.')
    if selected:
        return API_URI_SHORTCUTS[selected[0]]
    if api_uri is not None:
        return api_uri
    return PROD_API_URI


def setup_logging(verbosity, color=True):
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
                    # `--no-color` governs the log prefix too. Without the flag here it
                    # styled unconditionally, so `polyswarm --no-color -v …` still emitted a
                    # green prefix on a tty — the same half-honoured flag the formatters had.
                    prefix = f'{level} [{record.name}]: '
                    if color:
                        prefix = click.style(prefix, **self.colors[level])
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
            return super().invoke(ctx)
        except (
                exceptions.NoResultsException,
                exceptions.NotFoundException,
                api_exceptions.NoResultsException,
                api_exceptions.NotFoundException,
                api_exceptions.FailedInstanceException,
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
            # Transport errors come from the SDK's HTTP dependency (httpx; requests
            # historically), so match by ancestry name instead of importing those
            # libraries here. httpx roots every request/transport/status error at
            # HTTPError; requests rooted everything at RequestException; the builtin
            # ConnectionError and ssl.SSLError cover raw socket/TLS failures.
            if {'HTTPError', 'RequestException', 'ConnectionError', 'SSLError'} \
                    & {c.__name__ for c in type(e).__mro__}:
                logger.error(e)
                logger.error('Unhandled exception happened. Please contact support if the error persists.')
                raise Exit(1)
            else:
                logger.exception(e)
                logger.error('Unhandled exception happened. Please contact support.')
                raise Exit(2)


@click.group(cls=ExceptionHandlingGroup, context_settings=CONTEXT_SETTINGS)
@click.option('-a', '--api-key', help='Your API key for polyswarm.network (required).',
              default='', callback=validate_key, envvar='POLYSWARM_API_KEY', show_envvar=True)
@click.option('-u', '--api-uri', default=None,
              envvar='POLYSWARM_API_URI', show_envvar=True,
              help='The API endpoint (ADVANCED). Defaults to the production API. '
                   'Mutually exclusive with --prod/--stage/--local/--prod-eu/--stage-eu.')
@click.option('--prod', is_flag=True, default=False,
              help='Target the production API (https://api.polyswarm.network/v3) — same as the default.')
@click.option('--stage', is_flag=True, default=False,
              help='Target the US staging API (https://api.stage-blue.polyswarm.network/v3).')
@click.option('--local', is_flag=True, default=False,
              help='Target a local API (http://localhost:9696/v3).')
@click.option('--prod-eu', 'prod_eu', is_flag=True, default=False,
              help='Target the EU production API (https://api.prod-eu-v3.polyswarm.network/v3).')
@click.option('--stage-eu', 'stage_eu', is_flag=True, default=False,
              help='Target the EU staging API (https://api.stage-eu-blue.polyswarm.network/v3).')
@click.option('-o', '--output-file', type=click.File('w', encoding='utf8'), help='Path to output file.')
@click.option('--output-format', '--fmt', default='text', type=click.Choice(formatters.keys()),
              help='Output format. Human-readable text or JSON.')
@click.option('--color/--no-color', default=True, help='Use colored output in text mode.')
@click.option('-v', '--verbose', default=0, count=True)
@click.option('-c', '--community', default='default', envvar='POLYSWARM_COMMUNITY',
              help='Community to use.', show_envvar=True)
@click.option('--parallel', default=8, help='Number of threads to be used in parallel http requests.')
@click.option('--verify/--no-verify', default=True, help='Verify TLS connections.')
@click.version_option(polyswarm.__version__, '--version', prog_name='polyswarm-cli')
@click.version_option(polyswarm_api.__version__, '--api-version', prog_name='polyswarm-api')
@click.pass_context
def polyswarm_cli(ctx, api_key, api_uri, output_file, output_format, color, verbose, community, parallel, verify,
                  prod, stage, local, prod_eu, stage_eu):
    """
    This is a PolySwarm CLI client, which allows you to interact directly
    with the PolySwarm network to scan files, search hashes, and more.
    """
    setup_logging(verbose, color=color)
    logger.info('Running polyswarm-cli version %s with polyswarm-api version %s',
                polyswarm.__version__, polyswarm_api.__version__)

    ctx.obj = {}

    if ctx.invoked_subcommand is None:
        return

    output_file = output_file or click.get_text_stream('stdout')

    api_uri_from_cli = ctx.get_parameter_source('api_uri') == ParameterSource.COMMANDLINE
    api_uri = resolve_api_uri(api_uri, api_uri_from_cli,
                              {'prod': prod, 'stage': stage, 'local': local,
                               'prod_eu': prod_eu, 'stage_eu': stage_eu})

    ctx.obj['api'] = Polyswarm(api_key, uri=api_uri, community=community, parallel=parallel, verify=verify)
    ctx.obj['output'] = formatters[output_format](color=color, output=output_file)


commands = [
    scan, wait, lookup, search, live, historical,
    download, download_id, download_sandbox_artifact,
    cat, stream, rescan, rescan_id,
    rules, link, tag, family, metadata,
    engine, known, sandbox, sandbox_list,
    activity, report, report_template, account, bundle, notification, sample,
    kgb,
]

for command in commands:
    polyswarm_cli.add_command(command)
