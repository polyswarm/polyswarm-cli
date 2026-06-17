"""Tests for --api-uri endpoint resolution and the convenience environment
shortcuts (--stage / --local / --prod-eu / --stage-eu).

Precedence under test:

    explicit command-line flag  >  POLYSWARM_API_URI env var  >  production default

- a shortcut wins over an ambient POLYSWARM_API_URI;
- a shortcut conflicts with an explicit command-line --api-uri (mutually exclusive);
- a command-line --api-uri wins over the env var;
- shortcuts are mutually exclusive with each other.

resolve_api_uri is unit-tested directly; the CLI integration tests drive the
real option parsing (incl. the env var via CliRunner's `env=`) and assert the
resolved endpoint reaches the client.
"""
from unittest import TestCase, mock
from unittest.mock import MagicMock

import click
from click.testing import CliRunner

from polyswarm.client import polyswarm as client
from polyswarm.client.polyswarm import resolve_api_uri, PROD_API_URI, API_URI_SHORTCUTS


_API_KEY = '1' * 32
_ENV_URI = 'http://env.example.test/v3'
_CLI_URI = 'http://cli.example.test/v3'


def _shortcuts(stage=False, local=False, prod_eu=False, stage_eu=False):
    return {'stage': stage, 'local': local, 'prod_eu': prod_eu, 'stage_eu': stage_eu}


class ResolveApiUriTest(TestCase):
    def test_default_is_production(self):
        assert resolve_api_uri(None, False, _shortcuts()) == PROD_API_URI
        assert PROD_API_URI == 'https://api.polyswarm.network/v3'

    def test_explicit_cli_api_uri_passthrough(self):
        assert resolve_api_uri(_CLI_URI, True, _shortcuts()) == _CLI_URI

    def test_env_api_uri_used_when_no_flag(self):
        # api_uri came from the env var (not the command line) -> used as-is.
        assert resolve_api_uri(_ENV_URI, False, _shortcuts()) == _ENV_URI

    def test_each_shortcut_resolves(self):
        expected = {
            'stage': 'https://api.stage-v3.polyswarm.network/v3',
            'local': 'http://localhost:9696/v3',
            'prod_eu': 'https://api.prod-eu-v3.polyswarm.network/v3',
            'stage_eu': 'https://api.stage-eu-v3.polyswarm.network/v3',
        }
        # guard against the constant drifting from the verified ingress hosts
        assert API_URI_SHORTCUTS == expected
        for name, url in expected.items():
            assert resolve_api_uri(None, False, _shortcuts(**{name: True})) == url, name

    def test_shortcut_wins_over_env_var(self):
        # env-derived api_uri present, but the shortcut flag is explicit -> flag wins.
        assert resolve_api_uri(_ENV_URI, False, _shortcuts(stage=True)) == API_URI_SHORTCUTS['stage']

    def test_shortcut_conflicts_with_cli_api_uri(self):
        with self.assertRaises(click.UsageError):
            resolve_api_uri(_CLI_URI, True, _shortcuts(stage=True))

    def test_two_shortcuts_are_mutually_exclusive(self):
        with self.assertRaises(click.UsageError):
            resolve_api_uri(None, False, _shortcuts(stage=True, local=True))


class ApiUriCliTest(TestCase):
    """End-to-end through the real option parser: invoke `metadata analyze-ip`
    (which builds `{uri}/instance/url` via the real Polyswarm.submit_url) with
    the SDK's _single mocked, and read back the base endpoint the client used."""

    def setUp(self):
        self.cli = CliRunner()

    def _resolved_base(self, *global_opts, env=None):
        fake = MagicMock()
        fake.json = {'id': 1}
        with mock.patch('polyswarm_api.api.PolyswarmAPI._single', return_value=fake) as m:
            result = self.cli.invoke(
                client.polyswarm_cli,
                ['-a', _API_KEY, *global_opts, '--output-format', 'json',
                 'metadata', 'analyze-ip', '1.2.3.4'],
                env=env,
                catch_exceptions=False,
            )
        assert result.exit_code == 0, result.output
        url = m.call_args.args[0]['url']
        assert url.endswith('/instance/url'), url
        return url[:-len('/instance/url')]

    def _error(self, *global_opts, env=None):
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, *global_opts, 'metadata', 'analyze-ip', '1.2.3.4'],
            env=env,
        )

    # --- precedence path ---
    def test_default_targets_production(self):
        assert self._resolved_base() == 'https://api.polyswarm.network/v3'

    def test_env_var_used_when_no_flag(self):
        assert self._resolved_base(env={'POLYSWARM_API_URI': _ENV_URI}) == _ENV_URI

    def test_cli_api_uri_beats_env_var(self):
        assert self._resolved_base('--api-uri', _CLI_URI,
                                   env={'POLYSWARM_API_URI': _ENV_URI}) == _CLI_URI

    def test_shortcut_beats_env_var(self):
        assert self._resolved_base('--stage',
                                   env={'POLYSWARM_API_URI': _ENV_URI}) == API_URI_SHORTCUTS['stage']

    # --- each shortcut ---
    def test_stage_shortcut(self):
        assert self._resolved_base('--stage') == 'https://api.stage-v3.polyswarm.network/v3'

    def test_local_shortcut(self):
        assert self._resolved_base('--local') == 'http://localhost:9696/v3'

    def test_prod_eu_shortcut(self):
        assert self._resolved_base('--prod-eu') == 'https://api.prod-eu-v3.polyswarm.network/v3'

    def test_stage_eu_shortcut(self):
        assert self._resolved_base('--stage-eu') == 'https://api.stage-eu-v3.polyswarm.network/v3'

    def test_explicit_cli_api_uri(self):
        assert self._resolved_base('--api-uri', _CLI_URI) == _CLI_URI

    # --- mutual exclusion ---
    def test_shortcut_with_cli_api_uri_errors(self):
        result = self._error('--stage', '--api-uri', _CLI_URI)
        assert result.exit_code == 2
        assert 'api-uri' in result.output

    def test_two_shortcuts_error(self):
        result = self._error('--stage', '--stage-eu')
        assert result.exit_code == 2
        assert 'mutually exclusive' in result.output

    # Note: that an env var + shortcut does NOT error (the shortcut wins) is
    # proven by test_shortcut_beats_env_var, which asserts exit 0 + the resolved
    # URL via the _single-mocked path.
