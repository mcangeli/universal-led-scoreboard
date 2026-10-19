"""Verify restored data and preserve device configuration."""
import json
import tempfile
import unittest
from pathlib import Path
from universal_led.config_archive import export_portable, restore_portable
from universal_led.sport_settings import DEFAULT_SETTINGS


class VerifiedRestoreTests(unittest.TestCase):
    def test_restore_verifies_bytes_and_preserves_pi_hardware(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as target:
            source_path, target_path = Path(source), Path(target)
            (source_path / "settings.json").write_text(json.dumps(DEFAULT_SETTINGS))
            (target_path / "matrix.json").write_text('{"enabled":false,"brightness":40}')
            result = restore_portable(export_portable(source), target, ["settings"])
            self.assertTrue(result["verified"])
            self.assertTrue(result["restart_required"])
            self.assertEqual(json.loads((target_path / "settings.json").read_text()), DEFAULT_SETTINGS)
            self.assertEqual((target_path / "matrix.json").read_text(), '{"enabled":false,"brightness":40}')

    def test_restore_rejects_duplicate_section_selection(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as target:
            (Path(source) / "settings.json").write_text(json.dumps(DEFAULT_SETTINGS))
            with self.assertRaises(ValueError):
                restore_portable(export_portable(source), target, ["settings", "settings"])
            self.assertFalse((Path(target) / "settings.json").exists())


if __name__ == "__main__":
    unittest.main()
