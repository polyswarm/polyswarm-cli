"""Tests for the `kgb` (Known Good Binaries) CLI command group.

End-to-end CLI runs recorded against the live e2e stack (VCR replay), mirroring
cli_test.py. The internal-only KGB CRUD is reachable with the e2e gamma key.
Each test uses a distinct sha256 so it is independent and first-run-safe.
"""
import json

from tests.cli_test import BaseTestCase, vcr

SHA_A = 'a1' * 32  # text lifecycle
SHA_B = 'b2' * 32  # json
SHA_C = 'c3' * 32  # get-after-delete


class KgbTest(BaseTestCase):
    @vcr.use_cassette()
    def test_kgb_create_get_delete_text(self):
        created = self._run_cli(['--no-color', 'kgb', 'create', SHA_A, 'nsrl'])
        self.assertEqual(0, created.exit_code, created.output)
        assert SHA_A in created.output
        assert 'nsrl' in created.output

        got = self._run_cli(['--no-color', 'kgb', 'get', SHA_A])
        self.assertEqual(0, got.exit_code, got.output)
        assert SHA_A in got.output
        assert 'nsrl' in got.output

        deleted = self._run_cli(['--no-color', 'kgb', 'delete', SHA_A])
        self.assertEqual(0, deleted.exit_code, deleted.output)
        assert SHA_A in deleted.output
        assert 'Deleted' in deleted.output

    @vcr.use_cassette()
    def test_kgb_create_get_json(self):
        created = self._run_cli(['--fmt', 'json', 'kgb', 'create', SHA_B, 'winget'])
        self.assertEqual(0, created.exit_code, created.output)
        payload = json.loads(created.output.strip().splitlines()[-1])
        assert payload['sha256'] == SHA_B
        assert 'winget' in payload.get('sources', [])

        got = self._run_cli(['--fmt', 'json', 'kgb', 'get', SHA_B])
        self.assertEqual(0, got.exit_code, got.output)
        payload = json.loads(got.output.strip().splitlines()[-1])
        assert payload['sha256'] == SHA_B
        assert 'winget' in payload.get('sources', [])

    @vcr.use_cassette()
    def test_kgb_get_after_delete_not_found(self):
        created = self._run_cli(['--no-color', 'kgb', 'create', SHA_C, 'nsrl'])
        self.assertEqual(0, created.exit_code, created.output)

        deleted = self._run_cli(['--no-color', 'kgb', 'delete', SHA_C])
        self.assertEqual(0, deleted.exit_code, deleted.output)

        # The KnownGood row is gone; a retrieve now 404s -> NotFoundException -> exit 1.
        missing = self._run_cli(['--no-color', 'kgb', 'get', SHA_C])
        self.assertEqual(1, missing.exit_code, missing.output)
