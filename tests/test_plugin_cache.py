import tempfile
import unittest
from pathlib import Path
from universal_led.plugin_cache import invalidate_plugin_cache
from universal_led.configurator import HTML


class PluginCacheTests(unittest.TestCase):
    def test_only_json_files_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache = root / "daily-calendar"
            cache.mkdir()
            (cache / "feed.json").write_text("{}")
            (cache / "refresh.lock").write_text("lock")
            (cache / "notes.txt").write_text("keep")
            self.assertEqual(invalidate_plugin_cache("daily-calendar", root), 1)
            self.assertFalse((cache / "feed.json").exists())
            self.assertTrue((cache / "refresh.lock").exists())
            self.assertTrue((cache / "notes.txt").exists())

    def test_invalid_plugin_id_rejected(self):
        with self.assertRaises(ValueError):
            invalidate_plugin_cache("../other")

    def test_missing_cache_is_harmless(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(invalidate_plugin_cache("daily-calendar", tmp), 0)

    def test_calendar_refresh_button_present(self):
        self.assertIn("Refresh calendar now", HTML)
        self.assertIn("/api/plugins/cache/refresh", HTML)


if __name__ == "__main__":
    unittest.main()
