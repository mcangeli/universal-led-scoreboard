"""Native plugin process contract tests."""
import json
import tempfile
import unittest
from pathlib import Path
from universal_led.native_plugin_runtime import NativePluginSlot, enabled_screen_ids


class NativePluginRuntimeTests(unittest.TestCase):
    def test_enabled_screen_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugins"
            root.mkdir()
            for name in ("fish", "off"):
                folder = root / name
                folder.mkdir()
                (folder / "uls-plugin.json").write_text(json.dumps({
                    "id": name, "name": name, "version": "0.1.0",
                    "api_version": 1, "capabilities": ["screen"],
                    "entry_point": "sample:Screen"}))
            registry = Path(tmp) / "registry.json"
            registry.write_text(json.dumps({
                name: {"id": name, "version": "0.1.0",
                       "source": "https://github.com/example/sample",
                       "commit": "a" * 40, "enabled": name == "fish"}
                for name in ("fish", "off")}))
            self.assertEqual(enabled_screen_ids(root, registry), ("fish",))

    def test_slot_reads_persisted_display_duration(self):
        import shutil
        source = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "native-plugin"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugins"
            root.mkdir()
            shutil.copytree(source, root / "swimming-fish")
            from universal_led.plugin_settings_store import save_plugin_settings
            save_plugin_settings(root / "swimming-fish", root.parent / "plugin-settings",
                                 "swimming-fish", {"display_seconds": 27})
            slot = NativePluginSlot("swimming-fish", root)
            self.assertEqual(slot.display_seconds, 27)

    def test_fish_renders_in_subprocess(self):
        from pathlib import Path
        source = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "native-plugin"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import shutil
            shutil.copytree(source, root / "swimming-fish")
            slot = NativePluginSlot("swimming-fish", root, timeout=5)
            frame = slot.frame()
            self.assertEqual((frame.width, frame.height), (64, 32))
            self.assertTrue(any(pixel != (0, 12, 38) for row in frame.pixels for pixel in row))
            self.assertIsNone(slot.frame(live_games=True))


if __name__ == "__main__":
    unittest.main()
