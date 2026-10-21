"""Transactional plugin update regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led.plugin_install import install_local_plugin
from universal_led.plugin_manifest import ManifestError
from universal_led.plugin_registry import read_registry, set_plugin_enabled
from universal_led.plugin_update import update_local_plugin

SOURCE = "https://github.com/example/demo-plugin"
FIRST = "a" * 40
SECOND = "b" * 40


class PluginUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "plugins"
        self.root.mkdir()
        self.registry = self.base / "registry.json"
        self.package = self.base / "incoming"
        self.package.mkdir()
        self.write_package("1.0.0", "old")
        install_local_plugin(self.package, self.root, self.registry, SOURCE, FIRST)

    def write_package(self, version, marker):
        (self.package / "uls-plugin.json").write_text(json.dumps({
            "id": "demo-plugin", "name": "Demo", "version": version,
            "api_version": 1, "capabilities": ["screen"],
            "entry_point": "demo:Plugin",
        }))
        (self.package / "demo.py").write_text(marker)

    def test_update_preserves_enabled_state_and_external_settings(self):
        set_plugin_enabled(self.registry, "demo-plugin", True)
        settings = self.base / "plugin-settings"
        settings.mkdir()
        (settings / "demo-plugin.json").write_text('{"display_seconds": 22}')
        self.write_package("1.1.0", "new")
        record = update_local_plugin(self.package, self.root, self.registry, SOURCE, SECOND)
        self.assertTrue(record["enabled"])
        self.assertEqual(record["version"], "1.1.0")
        self.assertEqual(read_registry(self.registry)["demo-plugin"]["commit"], SECOND)
        self.assertEqual((self.root / "demo-plugin" / "demo.py").read_text(), "new")
        self.assertEqual((settings / "demo-plugin.json").read_text(), '{"display_seconds": 22}')

    def test_reject_changed_source_without_modifying_install(self):
        self.write_package("1.1.0", "new")
        with self.assertRaises(ManifestError):
            update_local_plugin(self.package, self.root, self.registry,
                                "https://github.com/example/other", SECOND)
        self.assertEqual((self.root / "demo-plugin" / "demo.py").read_text(), "old")
        self.assertEqual(read_registry(self.registry)["demo-plugin"]["commit"], FIRST)

    def test_reject_unsafe_package(self):
        self.write_package("1.1.0", "new")
        (self.package / "link.py").symlink_to(self.package / "demo.py")
        with self.assertRaises(ManifestError):
            update_local_plugin(self.package, self.root, self.registry, SOURCE, SECOND)
        self.assertEqual((self.root / "demo-plugin" / "demo.py").read_text(), "old")

    def test_registry_publish_failure_restores_original_package(self):
        self.write_package("1.1.0", "new")
        from universal_led import plugin_update
        actual_replace = plugin_update.os.replace

        def fail_registry_publish(src, dst):
            if Path(dst) == self.registry:
                raise OSError("simulated registry failure")
            return actual_replace(src, dst)

        with patch.object(plugin_update.os, "replace", side_effect=fail_registry_publish):
            with self.assertRaises(OSError):
                update_local_plugin(self.package, self.root, self.registry, SOURCE, SECOND)
        self.assertEqual((self.root / "demo-plugin" / "demo.py").read_text(), "old")
        self.assertEqual(read_registry(self.registry)["demo-plugin"]["commit"], FIRST)


if __name__ == "__main__":
    unittest.main()
