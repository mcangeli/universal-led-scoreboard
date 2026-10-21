import tempfile
import unittest
from pathlib import Path
from universal_led.plugin_settings_store import read_plugin_settings, save_plugin_settings
from universal_led.plugin_manifest import ManifestError


class PluginSettingsStoreTests(unittest.TestCase):
    def test_settings_survive_separate_package(self):
        package = Path(__file__).resolve().parents[1] / "plugins" / "swimming-fish"
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read_plugin_settings(package, tmp, "swimming-fish")["display_seconds"], 12)
            saved = save_plugin_settings(package, tmp, "swimming-fish",
                                         {"display_seconds": 27, "animation_speed": 2})
            self.assertEqual(saved["fish_color"], "gold")
            self.assertEqual(read_plugin_settings(package, tmp, "swimming-fish")["display_seconds"], 27)

    def test_invalid_settings_not_written(self):
        package = Path(__file__).resolve().parents[1] / "plugins" / "swimming-fish"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ManifestError):
                save_plugin_settings(package, tmp, "swimming-fish", {"display_seconds": -1})
            self.assertFalse((Path(tmp) / "swimming-fish.json").exists())


if __name__ == "__main__":
    unittest.main()
