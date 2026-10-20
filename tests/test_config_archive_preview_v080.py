"""Safe portable import preview regression coverage."""
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from universal_led.config_archive import export_portable, inspect_portable


class PortableImportPreviewTests(unittest.TestCase):
    def test_pi3_to_pi5_and_reverse_never_changes_hardware(self):
        with tempfile.TemporaryDirectory() as pi3, tempfile.TemporaryDirectory() as pi5:
            for root, enabled in ((pi3, True), (pi5, False)):
                path = Path(root)
                (path / "matrix.json").write_text(json.dumps({"enabled": enabled}))
                (path / "settings.json").write_text(json.dumps({"version": 1, "active_sport": "mlb" if enabled else "nhl"}))
            for source, destination in ((pi3, pi5), (pi5, pi3)):
                matrix = (Path(destination) / "matrix.json").read_bytes()
                result = inspect_portable(export_portable(source), destination)
                self.assertFalse(result["applied"])
                self.assertTrue(result["hardware_preserved"])
                self.assertEqual(result["sections"]["settings"]["action"], "replace")
                self.assertEqual((Path(destination) / "matrix.json").read_bytes(), matrix)

    def test_rejects_unexpected_hardware_file(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "settings.json").write_text('{"version":1}')
            original = export_portable(root)
            with zipfile.ZipFile(io.BytesIO(original)) as source:
                contents = {name: source.read(name) for name in source.namelist()}
            contents["matrix.json"] = b'{"enabled":true}'
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as archive:
                for name, data in contents.items():
                    archive.writestr(name, data)
            with self.assertRaises(ValueError):
                inspect_portable(buffer.getvalue(), root)

    def test_rejects_tampered_checksum(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "settings.json").write_text('{"version":1}')
            with zipfile.ZipFile(io.BytesIO(export_portable(root))) as source:
                contents = {name: source.read(name) for name in source.namelist()}
            contents["settings.json"] = b'{"version":2}'
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as archive:
                for name, data in contents.items():
                    archive.writestr(name, data)
            with self.assertRaises(ValueError):
                inspect_portable(buffer.getvalue(), root)

    def test_preview_identifies_unchanged_sections(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "settings.json").write_text('{"version":1}')
            result = inspect_portable(export_portable(root), root)
            self.assertEqual(result["sections"]["settings"]["action"], "unchanged")


if __name__ == "__main__":
    unittest.main()
