"""Local plugin installation safety and rollback regression tests."""
import json
import tempfile
import unittest
from pathlib import Path

from universal_led.plugin_install import install_local_plugin
from universal_led.plugin_manifest import ManifestError
from universal_led.plugin_registry import read_registry


MANIFEST = {
    "id": "demo-plugin", "name": "Demo Plugin", "version": "1.0.0",
    "api_version": 1, "capabilities": ["screen"], "entry_point": "demo:Plugin",
}
SOURCE = "https://github.com/example/demo-plugin"
COMMIT = "b" * 40


class LocalPluginInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.package = self.base / "download"
        self.package.mkdir()
        (self.package / "uls-plugin.json").write_text(json.dumps(MANIFEST))
        (self.package / "demo.py").write_text("class Plugin: pass\n")
        self.root = self.base / "plugins"
        self.root.mkdir()
        self.registry = self.base / "installed.json"

    def install(self):
        return install_local_plugin(self.package, self.root, self.registry, SOURCE, COMMIT)

    def test_install_publishes_disabled_plugin_and_registry(self):
        record = self.install()
        self.assertFalse(record["enabled"])
        self.assertTrue((self.root / "demo-plugin" / "demo.py").exists())
        self.assertEqual(read_registry(self.registry)["demo-plugin"], record)

    def test_duplicate_install_does_not_replace_files(self):
        self.install()
        with self.assertRaises(ManifestError):
            self.install()
        self.assertEqual(read_registry(self.registry)["demo-plugin"]["commit"], COMMIT)

    def test_reject_symlink_without_publishing(self):
        (self.package / "outside.py").symlink_to(self.base / "outside.py")
        with self.assertRaises(ManifestError):
            self.install()
        self.assertFalse((self.root / "demo-plugin").exists())
        self.assertFalse(self.registry.exists())

    def test_invalid_source_does_not_modify_installation(self):
        with self.assertRaises(ManifestError):
            install_local_plugin(self.package, self.root, self.registry,
                                 "https://example.com/other", COMMIT)
        self.assertFalse((self.root / "demo-plugin").exists())


if __name__ == "__main__":
    unittest.main()
