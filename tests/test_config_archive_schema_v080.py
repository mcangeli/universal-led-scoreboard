"""Schema validation must precede any portable restore."""
import json
import tempfile
import unittest
from pathlib import Path

from universal_led.config_archive import export_portable, validate_portable_sections
from universal_led.sport_settings import DEFAULT_SETTINGS


class PortableSchemaTests(unittest.TestCase):
    def test_valid_sport_settings_preview_without_write(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as destination:
            (Path(source) / "settings.json").write_text(json.dumps(DEFAULT_SETTINGS))
            (Path(destination) / "matrix.json").write_text('{"enabled":false}')
            preview = validate_portable_sections(export_portable(source), destination)
            self.assertTrue(preview["schema_valid"])
            self.assertFalse(preview["applied"])
            self.assertEqual((Path(destination) / "matrix.json").read_text(), '{"enabled":false}')
            self.assertFalse((Path(destination) / "settings.json").exists())

    def test_invalid_settings_rejected_without_write(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as destination:
            (Path(source) / "settings.json").write_text('{"version":1}')
            with self.assertRaises(ValueError):
                validate_portable_sections(export_portable(source), destination)
            self.assertFalse((Path(destination) / "settings.json").exists())

    def test_unknown_nhl_team_rejected(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as destination:
            (Path(source) / "nhl_teams.json").write_text('{"NOT_A_TEAM":{"primary":"#112233"}}')
            with self.assertRaises(ValueError):
                validate_portable_sections(export_portable(source), destination)
            self.assertFalse((Path(destination) / "nhl_teams.json").exists())


if __name__ == "__main__":
    unittest.main()
