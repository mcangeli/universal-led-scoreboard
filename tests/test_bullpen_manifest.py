"""Bullpen metadata discovery regression tests."""
import tempfile
import unittest
from pathlib import Path

from universal_led.bullpen_manifest import inspect_bullpen_metadata
from universal_led.plugin_manifest import ManifestError


VALID = """[project]
name = "mlb-led-scoreboard-magic-number"
version = "0.3.1"
description = "Division and Wild Card magic numbers"

[project.entry-points."bullpen.mlbled.plugin"]
"magic_number" = "mlb_led_scoreboard_magic_number:load"
"""


class BullpenManifestTests(unittest.TestCase):
    def test_magic_number_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "pyproject.toml").write_text(VALID)
            metadata = inspect_bullpen_metadata(Path(tmp))
            self.assertEqual(metadata["id"], "magic_number")
            self.assertEqual(metadata["entry_point"], "mlb_led_scoreboard_magic_number:load")
            self.assertEqual(metadata["version"], "0.3.1")
            self.assertEqual(metadata["format"], "bullpen")
            self.assertFalse(metadata["installable"])

    def test_rejects_invalid_entry_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "pyproject.toml").write_text(VALID.replace(":load", ":load;exec"))
            with self.assertRaises(ManifestError):
                inspect_bullpen_metadata(Path(tmp))

    def test_rejects_multiple_entry_points(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "pyproject.toml").write_text(VALID + '"another" = "package:load"\\n')
            with self.assertRaises(ManifestError):
                inspect_bullpen_metadata(Path(tmp))

    def test_rejects_missing_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ManifestError):
                inspect_bullpen_metadata(Path(tmp))


if __name__ == "__main__":
    unittest.main()
