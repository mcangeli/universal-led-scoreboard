"""Read-only installed plugin inventory regression tests."""
import json
import tempfile
import unittest
from pathlib import Path

from universal_led.plugin_inventory import installed_plugin_inventory


class PluginInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "plugins"
        self.root.mkdir()
        self.registry = Path(self.temp.name) / "registry.json"
        self.record = {
            "id": "example", "version": "1.0.0",
            "source": "https://github.com/example/example",
            "commit": "a" * 40, "enabled": False,
        }
        self.registry.write_text(json.dumps({"example": self.record}))
        self.folder = self.root / "example"
        self.folder.mkdir()
        self.manifest = self.folder / "uls-plugin.json"
        self.manifest.write_text(json.dumps({
            "id": "example", "name": "Example", "version": "1.0.0",
            "api_version": 1, "capabilities": ["screen"],
            "entry_point": "example:Screen",
        }))

    def test_valid_disabled_plugin(self):
        item = installed_plugin_inventory(self.root, self.registry)["plugins"][0]
        self.assertEqual((item["name"], item["status"], item["error"]), ("Example", "disabled", None))

    def test_enabled_plugin(self):
        self.record["enabled"] = True
        self.registry.write_text(json.dumps({"example": self.record}))
        self.assertEqual(installed_plugin_inventory(self.root, self.registry)["plugins"][0]["status"], "enabled")

    def test_missing_package(self):
        self.manifest.unlink()
        item = installed_plugin_inventory(self.root, self.registry)["plugins"][0]
        self.assertEqual(item["status"], "error")
        self.assertIn("missing", item["error"])

    def test_version_mismatch(self):
        data = json.loads(self.manifest.read_text())
        data["version"] = "2.0.0"
        self.manifest.write_text(json.dumps(data))
        self.assertIn("version", installed_plugin_inventory(self.root, self.registry)["plugins"][0]["error"])

    def test_unregistered_package(self):
        self.registry.write_text("{}")
        result = installed_plugin_inventory(self.root, self.registry)
        self.assertEqual(result["unregistered"], ["example"])
        self.assertEqual(result["plugins"], [])

    def test_does_not_change_registry(self):
        before = self.registry.read_bytes()
        installed_plugin_inventory(self.root, self.registry)
        self.assertEqual(self.registry.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
