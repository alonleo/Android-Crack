#!/usr/bin/env python3
"""Exercise SDK registry CRUD against isolated temporary YAML copies."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'skills/common/scripts/lib'))
import common
SKILL = Path(__file__).resolve().parents[1]
CLI = Path(__file__).with_name('manage-sdk-registry.py')


class RegistryTests(unittest.TestCase):
    def test_generated_markdown_and_sync(self):
        self.call('sync-doc')
        document = self.registry.with_suffix('.md')
        before = document.read_bytes()
        self.call('add', '--section', 'engine_so_keep', '--name', 'libmarkdown.so')
        self.assertIn('libmarkdown.so', document.read_text(encoding='utf-8'))
        self.assertNotEqual(before, document.read_bytes())
        self.call('validate')
        document.write_text('stale', encoding='utf-8')
        self.call('validate', ok=False)
        self.call('sync-doc')
        self.call('validate')

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix='sdk-crud-')
        self.addCleanup(self.folder.cleanup)
        self.registry = Path(self.folder.name) / 'registry.yaml'
        self.registry.write_bytes((SKILL / 'references/third-party-sdk-removal-registry.yaml').read_bytes())

    def call(self, operation, *args, ok=True):
        result = subprocess.run([sys.executable, str(CLI), operation, '--registry', str(self.registry), *args],
                                capture_output=True, text=True, encoding='utf-8',
                                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)

    def test_string_crud_and_queries(self):
        args = ('--section', 'engine_so_keep', '--name', 'libcrud.so')
        self.call('add', *args)
        self.assertEqual(self.call('get', *args)['entry'], 'libcrud.so')
        self.assertIn('libcrud.so', self.call('list', '--section', 'engine_so_keep')['entries'])
        self.call('update', *args, '--new-name', 'librenamed.so')
        self.call('get', *args, ok=False)
        self.call('delete', '--section', 'engine_so_keep', '--name', 'librenamed.so')
        self.call('get', '--section', 'engine_so_keep', '--name', 'librenamed.so', ok=False)

    def test_mapping_update_preserves_other_fields(self):
        args = ('--section', 'build_config_stubs', '--name', 'com/check/BuildConfig.java')
        self.call('add', *args, '--package', 'com.check', '--why', 'initial')
        self.call('update', *args, '--why', 'revised')
        self.assertEqual(self.call('get', *args)['entry']['package'], 'com.check')
        self.assertEqual(self.call('get', *args)['entry']['why'], 'revised')
        self.call('delete', *args)

    def test_idempotent_add_and_no_implicit_overwrite(self):
        args = ('--section', 'manifest_drop_exact', '--name', 'example.InitProvider')
        self.call('add', *args, '--why', 'first')
        before = self.registry.read_bytes()
        self.assertFalse(self.call('add', *args, '--why', 'second')['changed'])
        self.assertEqual(self.registry.read_bytes(), before)

    def test_errors_do_not_write(self):
        before = self.registry.read_bytes()
        self.call('add', '--section', 'build_config_stubs', '--name', 'foo', ok=False)
        self.call('update', '--section', 'engine_so_keep', '--name', 'absent', '--new-name', 'other', ok=False)
        self.call('delete', '--section', 'engine_so_keep', '--name', 'absent', ok=False)
        self.call('add', '--section', 'engine_so_keep', '--name', '   ', ok=False)
        self.assertEqual(before, self.registry.read_bytes())

    def test_dry_run_and_rename_collision(self):
        args = ('--section', 'engine_so_keep', '--name', 'libcrud.so')
        before = self.registry.read_bytes()
        self.call('add', *args, '--dry-run')
        self.assertEqual(before, self.registry.read_bytes())
        self.call('add', *args)
        self.call('add', '--section', 'engine_so_keep', '--name', 'libother.so')
        before = self.registry.read_bytes()
        self.call('update', *args, '--new-name', 'libother.so', ok=False)
        self.assertEqual(before, self.registry.read_bytes())

    def test_readonly(self):
        before = self.registry.read_bytes()
        self.call('list')
        self.assertEqual(before, self.registry.read_bytes())

    def test_metadata_value_update(self):
        args = ('--section', 'meta_data_force_value', '--name', 'example.enabled')
        self.call('add', *args, '--value', 'false', '--why', 'disabled')
        self.call('update', *args, '--value', 'true')
        entry = self.call('get', *args)['entry']
        self.assertEqual(entry['value'], 'true')
        self.assertEqual(entry['why'], 'disabled')

    def test_existing_writer_lock_preserves_data(self):
        lock = self.registry.with_name(self.registry.name + '.lock')
        lock.write_text('other writer', encoding='utf-8')
        before = self.registry.read_bytes()
        self.call('add', '--section', 'engine_so_keep', '--name', 'liblocked.so', ok=False)
        self.assertEqual(before, self.registry.read_bytes())
        self.assertTrue(lock.exists())

    def test_invalid_schema_does_not_write(self):
        self.registry.write_text('schema_version: 1\nengine_so_keep: wrong\n', encoding='utf-8')
        before = self.registry.read_bytes()
        self.call('list', ok=False)
        self.assertEqual(before, self.registry.read_bytes())


if __name__ == '__main__':
    common._REPO_ROOT = ROOT
    common.ensure_env()
    common.log_info('Testing SDK registry on temporary copies only')
    unittest.main()
