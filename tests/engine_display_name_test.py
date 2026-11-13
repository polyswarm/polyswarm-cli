"""Pure-unit tests: text output labels assertions with the engine display name, JSON keeps the name."""
import json
from io import StringIO

import click
from polyswarm_api import resources

from polyswarm.formatters.json import JSONOutput
from polyswarm.formatters.text import TextOutput

SHA = 'a' * 64


def _assertion(verdict, mask=True, metadata=None, display_name='DefenceNet'):
    engine = {'name': 'DefenseNet'}
    if display_name is not None:
        engine['display_name'] = display_name
    return {
        'author': '0x' + 'd' * 40, 'author_name': 'DefenseNet', 'engine': engine,
        'bid': '1000000000000000', 'mask': mask, 'metadata': metadata, 'verdict': verdict,
    }


def _instance(assertion):
    return resources.ArtifactInstance({
        'sha256': SHA, 'md5': 'c' * 32, 'sha1': 'b' * 40,
        'mimetype': 'application/x-dosexec', 'size': 68, 'extended_type': '',
        'first_seen': '2020-01-01T00:00:00', 'upload_url': '', 'metadata': [],
        'id': '111', 'community': 'gamma', 'assertions': [assertion], 'votes': [],
        'failed': False, 'window_closed': True, 'polyscore': None,
    })


def _render(instance):
    return click.unstyle('\n'.join(TextOutput(color=False).artifact_instance(instance, write=False)))


class TestTextUsesDisplayName:
    def test_clean(self):
        text = _render(_instance(_assertion(False)))
        assert 'DefenceNet: Clean' in text
        assert 'DefenseNet' not in text

    def test_no_response(self):
        text = _render(_instance(_assertion(None)))
        assert 'DefenceNet: Engine chose not to respond to this bounty.' in text
        assert 'DefenseNet' not in text

    def test_malicious_with_metadata(self):
        text = _render(_instance(_assertion(True, metadata={'malware_family': 'x'})))
        assert 'DefenceNet: Malicious, metadata: {"malware_family": "x"}' in text
        assert 'DefenseNet' not in text

    def test_missing_display_name_degrades_to_name(self):
        text = _render(_instance(_assertion(False, display_name=None)))
        assert 'DefenseNet: Clean' in text


class TestJsonKeepsStableName:
    def test_engine_name_is_the_raw_payload(self):
        out = StringIO()
        JSONOutput(output=out).artifact_instance(_instance(_assertion(False)))
        engine = json.loads(out.getvalue())['assertions'][0]['engine']
        assert engine['name'] == 'DefenseNet'
