"""Managed installation of bundled Hello World example."""
import tempfile
import unittest
from pathlib import Path

from universal_led.example_plugin_install import install_example
from universal_led.plugin_inventory import installed_plugin_inventory
from universal_led.plugin_registry import set_plugin_enabled, read_registry
from universal_led.plugin_manifest import ManifestError


class HelloWorldManagedInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "plugins"
        self.root.mkdir()
        self.registry = Path(self.temp.name) / "plugins.json"

    def test_install_is_disabled_and_discoverable(self):
        record = install_example(self.root, self.registry)
        self.assertFalse(record["enabled"])
        item = installed_plugin_inventory(self.root, self.registry)["plugins"][0]
        self.assertEqual((item["id"], item["status"], item["error"]), ("hello-world", "disabled", None))

    def test_enable_and_disable_preserve_package(self):
        install_example(self.root, self.registry)
        set_plugin_enabled(self.registry, "hello-world", True)
        self.assertEqual(installed_plugin_inventory(self.root, self.registry)["plugins"][0]["status"], "enabled")
        set_plugin_enabled(self.registry, "hello-world", False)
        self.assertFalse(read_registry(self.registry)["hello-world"]["enabled"])
        self.assertTrue((self.root / "hello-world" / "hello_world.py").exists())

    def test_first_install_creates_missing_plugin_directory(self):
        self.root.rmdir()
        self.assertFalse(self.root.exists())
        record = install_example(self.root, self.registry)
        self.assertEqual(record["id"], "hello-world")
        self.assertTrue((self.root / "hello-world" / "uls-plugin.json").is_file())
        self.assertFalse(record["enabled"])

    def test_does_not_create_unrelated_parent_directories(self):
        missing = Path(self.temp.name) / "missing" / "plugins"
        with self.assertRaises(ManifestError):
            install_example(missing, self.registry)
        self.assertFalse(missing.exists())

    def test_reinstallation_is_refused(self):
        install_example(self.root, self.registry)
        with self.assertRaises(ManifestError):
            install_example(self.root, self.registry)


if __name__ == "__main__":
    unittest.main()
