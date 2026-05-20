"""Tests for the metadata field-property CLI commands.

These tests mock the SDK methods directly to keep the test runtime
self-contained (no live artifact-index, no VCR cassettes).
"""
from unittest import TestCase, mock
from unittest.mock import MagicMock

from click.testing import CliRunner

from polyswarm.client import polyswarm as client


_API_KEY = '1' * 32
_API_URL = 'http://artifact-index-e2e:9696/v3'
_COMMUNITY = 'gamma'


def _fake_resource(field_path='polyunite.malware_family',
                   description='Identified malware family',
                   example='polyunite.malware_family:lockbit',
                   category='polyunite',
                   aliases=None):
    obj = MagicMock()
    obj.field_path = field_path
    obj.description = description
    obj.example = example
    obj.category = category
    obj.aliases = aliases
    obj.created = '2026-05-20T00:00:00'
    obj.updated = '2026-05-20T00:00:00'
    obj.json = {
        'field_path': field_path,
        'description': description,
        'example': example,
        'category': category,
        'aliases': aliases,
    }
    return obj


class FieldPropertyCliTest(TestCase):
    def setUp(self):
        self.cli = CliRunner()

    def _run(self, *cmd):
        return self.cli.invoke(
            client.polyswarm_cli,
            ['-a', _API_KEY, '-u', _API_URL, '-c', _COMMUNITY] + list(cmd),
            catch_exceptions=False,
        )

    def test_field_property_create(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.metadata_field_properties_create',
                        return_value=_fake_resource()) as m:
            result = self._run('search', 'field-property', 'create',
                               'polyunite.malware_family',
                               '--description', 'Identified malware family',
                               '--example', 'polyunite.malware_family:lockbit',
                               '--category', 'polyunite')
        assert result.exit_code == 0, result.output
        m.assert_called_once()
        kwargs = m.call_args.kwargs
        assert kwargs['field_path'] == 'polyunite.malware_family'
        assert kwargs['description'] == 'Identified malware family'
        assert kwargs['example'] == 'polyunite.malware_family:lockbit'
        assert kwargs['category'] == 'polyunite'
        assert kwargs['aliases'] is None
        assert 'polyunite.malware_family' in result.output

    def test_field_property_create_with_aliases(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.metadata_field_properties_create',
                        return_value=_fake_resource(aliases=['family', 'malware'])) as m:
            result = self._run('search', 'field-property', 'create',
                               'polyunite.malware_family',
                               '--description', 'd',
                               '--alias', 'family',
                               '--alias', 'malware')
        assert result.exit_code == 0, result.output
        kwargs = m.call_args.kwargs
        assert kwargs['aliases'] == ['family', 'malware']

    def test_field_property_get(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.metadata_field_properties_get',
                        return_value=_fake_resource()) as m:
            result = self._run('search', 'field-property', 'get',
                               'polyunite.malware_family')
        assert result.exit_code == 0, result.output
        m.assert_called_once_with(field_path='polyunite.malware_family')
        assert 'Identified malware family' in result.output

    def test_field_property_update(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.metadata_field_properties_update',
                        return_value=_fake_resource(description='new desc')) as m:
            result = self._run('search', 'field-property', 'update',
                               'polyunite.malware_family',
                               '--description', 'new desc')
        assert result.exit_code == 0, result.output
        kwargs = m.call_args.kwargs
        assert kwargs['field_path'] == 'polyunite.malware_family'
        assert kwargs['description'] == 'new desc'
        assert kwargs['example'] is None
        assert kwargs['category'] is None
        assert kwargs['aliases'] is None
        assert 'new desc' in result.output

    def test_field_property_delete(self):
        with mock.patch('polyswarm_api.api.PolyswarmAPI.metadata_field_properties_delete',
                        return_value=_fake_resource()) as m:
            result = self._run('search', 'field-property', 'delete',
                               'polyunite.malware_family')
        assert result.exit_code == 0, result.output
        m.assert_called_once_with(field_path='polyunite.malware_family')

    def test_field_property_list(self):
        rows = [
            _fake_resource(field_path='apkid.files.filename', description='APK files'),
            _fake_resource(field_path='artifact.id', description='Artifact ID'),
        ]
        with mock.patch('polyswarm_api.api.PolyswarmAPI.metadata_field_properties_list',
                        return_value=iter(rows)) as m:
            result = self._run('search', 'field-property', 'list')
        assert result.exit_code == 0, result.output
        m.assert_called_once_with()
        assert 'apkid.files.filename' in result.output
        assert 'artifact.id' in result.output
