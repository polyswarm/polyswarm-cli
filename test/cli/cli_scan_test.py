from unittest import TestCase
from test.utils.base_test_case import BaseTestCase

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
        self.bad_hash = 'lmao'
        self.bad_file = '/tmp/never_gonna_give_you_up'
        self.bad_uuid = 'never-gonna-let-you-down'

    def test_rescan_invalid_hash(self):
        commands = ['rescan', self.bad_hash]
        self._do_fail_test([], 'text', None, commands)

    def test_scan_invalid_file(self):
        commands = ['scan', self.bad_file]
        self._do_fail_test([], 'text', None, commands)

    def test_lookup_invalid_uuid(self):
        commands = ['lookup', self.bad_uuid]
        self._do_fail_test([], 'text', None, commands)
