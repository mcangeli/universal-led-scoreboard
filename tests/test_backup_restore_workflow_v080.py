"""Backup import API and selective restore regression tests."""
import inspect
import json
import tempfile
import unittest
from pathlib import Path

from universal_led import configurator
from universal_led.config_archive import export_portable, restore_portable
from universal_led.sport_settings import DEFAULT_SETTINGS


class RestoreWorkflowTests(unittest.TestCase):
    def test_restore_selected_section_preserves_hardware_and_other_sections(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as destination:
            src,dst=Path(source),Path(destination)
            (src/'settings.json').write_text(json.dumps(DEFAULT_SETTINGS))
            (src/'teams.json').write_text('{}')
            (dst/'matrix.json').write_text('{"enabled":false}')
            (dst/'teams.json').write_text('{}')
            result=restore_portable(export_portable(src),dst,['settings'])
            self.assertEqual(result['sections'],['settings'])
            self.assertEqual(json.loads((dst/'settings.json').read_text()),DEFAULT_SETTINGS)
            self.assertEqual(json.loads((dst/'matrix.json').read_text()),{'enabled':False})
            self.assertEqual((dst/'teams.json').read_text(),'{}')
            self.assertTrue(Path(result['recovery_directory']).is_dir())

    def test_unapproved_restore_section_is_rejected(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as destination:
            (Path(source)/'settings.json').write_text(json.dumps(DEFAULT_SETTINGS))
            with self.assertRaises(ValueError):
                restore_portable(export_portable(source),destination,['matrix'])
            self.assertFalse((Path(destination)/'matrix.json').exists())

    def test_dashboard_import_requires_auth_and_token(self):
        source=inspect.getsource(configurator)
        self.assertIn("'/api/backup/preview','/api/backup/restore'",source)
        self.assertIn("validate_portable_sections(archive_bytes,config_dir)",source)
        self.assertIn("data.get('confirm') is not True",source)
        self.assertIn('id="import-backup-file"',source)
        self.assertIn('onclick="applyBackup()"',source)


if __name__ == '__main__':
    unittest.main()
