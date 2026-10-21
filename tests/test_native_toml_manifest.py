"""Native TOML manifest transition tests."""
import json
import tempfile
import unittest
from pathlib import Path
from universal_led.plugin_manifest import load_plugin_manifest, ManifestError

DATA = {"id":"example","name":"Example","version":"1.0.0","api_version":1,"capabilities":["screen"],"entry_point":"example:Screen"}

class NativeTomlManifestTests(unittest.TestCase):
    def test_toml(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,"uls-plugin.toml").write_text('id = "example"\nname = "Example"\nversion = "1.0.0"\napi_version = 1\ncapabilities = ["screen"]\nentry_point = "example:Screen"\n')
            self.assertEqual(load_plugin_manifest(tmp).plugin_id, "example")

    def test_legacy_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,"uls-plugin.json").write_text(json.dumps(DATA))
            self.assertEqual(load_plugin_manifest(tmp).plugin_id, "example")

    def test_both_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,"uls-plugin.json").write_text(json.dumps(DATA))
            Path(tmp,"uls-plugin.toml").write_text('id = "example"')
            with self.assertRaises(ManifestError):
                load_plugin_manifest(tmp)

    def test_missing_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ManifestError):
                load_plugin_manifest(tmp)
