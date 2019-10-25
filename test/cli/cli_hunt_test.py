from unittest import TestCase
from polyswarm_api.types.hash import to_hash
from polyswarm_api.types.query import MetadataQuery
from .base import BaseTestCase

from click.testing import CliRunner
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

TestCase.maxDiff = None


class ScanTest(BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(ScanTest, self).__init__(*args, **kwargs)
        self.test_runner = CliRunner()
        self.bad_id = "never-gonna-run-around"

    def test_live_lookup_invalid(self):
        commands = ['live', 'results', self.bad_id]
        self._do_fail_test([], 'text', None, commands)

    def test_live_delete_invalid(self):
        commands = ['live', 'delete', self.bad_id]
        self._do_fail_test([], 'text', None, commands)

    def test_historical_lookup_invalid(self):
        commands = ['historical', 'results', self.bad_id]
        self._do_fail_test([], 'text', None, commands)

    def test_historical_delete_invalid(self):
        commands = ['historical', 'delete', self.bad_id]
        self._do_fail_test([], 'text', None, commands)
