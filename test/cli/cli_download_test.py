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
        self.bad_hash = 'never-gonna-run-around'
        self.bad_time = 'and-hurt-you'

    def test_download_invalid_hash(self):
        commands = ['download', self.bad_hash]
        self._do_fail_test([], 'text', None, commands)

    def test_cat_invalid_hash(self):
        commands = ['cat', self.bad_hash]
        self._do_fail_test([], 'text', None, commands)

    def test_stream_bad_since(self):
        commands = ['stream', '--since', self.bad_time]
        self._do_fail_test([], 'text', None, commands)
