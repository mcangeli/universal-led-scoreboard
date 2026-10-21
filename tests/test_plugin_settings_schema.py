import unittest
from pathlib import Path
from universal_led.plugin_settings_schema import (
    load_settings_schema, validate_settings_schema, validated_settings)
from universal_led.plugin_manifest import ManifestError


class PluginSettingsSchemaTests(unittest.TestCase):
    def test_swimming_fish_schema_and_defaults(self):
        package = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "native-plugin"
        fields = load_settings_schema(package)
        self.assertEqual(validated_settings(fields, {})["display_seconds"], 12)
        self.assertEqual(validated_settings(fields, {"display_seconds": 30})["display_seconds"], 30)

    def test_duration_cannot_be_omitted(self):
        with self.assertRaises(ManifestError):
            validate_settings_schema({"fields": {"speed": {"type": "number", "default": 1}}})

    def test_rejects_out_of_range_duration(self):
        fields = load_settings_schema(Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "native-plugin")
        with self.assertRaises(ManifestError):
            validated_settings(fields, {"display_seconds": 1000})

    def test_rejects_unknown_setting(self):
        fields = load_settings_schema(Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "native-plugin")
        with self.assertRaises(ManifestError):
            validated_settings(fields, {"unknown": True})


if __name__ == "__main__":
    unittest.main()
