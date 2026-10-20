"""Portable backup must not transfer physical Pi settings."""
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from universal_led.config_archive import export_portable


class PortableArchiveTests(unittest.TestCase):
    def test_portable_backup_excludes_hardware_and_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "settings.json").write_text('{"active_sport":"mlb"}')
            (root / "teams.json").write_text('{"ATL":{"primary":"#123456"}}')
            for name in ("matrix.json", "wifi.json", "auth.json", "sessions.json", "password.json"):
                (root / name).write_text('{"secret":"do-not-export"}')
            (root / "backups").mkdir()
            (root / "backups" / "matrix-old.json").write_text('{"secret":"old"}')
            with zipfile.ZipFile(io.BytesIO(export_portable(root))) as archive:
                names = set(archive.namelist())
                self.assertEqual(names, {"manifest.json", "settings.json", "teams.json"})
                self.assertNotIn(b"do-not-export", io.BytesIO(export_portable(root)).getvalue())
                manifest = json.loads(archive.read("manifest.json"))
                self.assertEqual(manifest["format_version"], 1)
                self.assertEqual(manifest["kind"], "portable-application-settings")
                for name in ("settings.json", "teams.json"):
                    self.assertEqual(
                        manifest["sections"][name]["sha256"],
                        hashlib.sha256(archive.read(name)).hexdigest())

    def test_invalid_json_rejected_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text("invalid")
            with self.assertRaises(ValueError):
                export_portable(directory)
            self.assertEqual(path.read_text(), "invalid")

    def test_oversized_section_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "settings.json").write_bytes(b" " * (1024 * 1024 + 1))
            with self.assertRaises(ValueError):
                export_portable(directory)


if __name__ == "__main__":
    unittest.main()
