import json
import time
import tempfile
import unittest
from pathlib import Path
from universal_led.official_plugin_catalog import read_official_catalog, dynamic_official_catalog
from universal_led.plugin_manifest import ManifestError


class OfficialPluginCatalogTests(unittest.TestCase):
    def test_only_optional_plugins_are_catalogued(self):
        entries = read_official_catalog()
        self.assertEqual([item["id"] for item in entries], ["swimming-fish", "disney-wait-times", "daily-calendar"])
        self.assertEqual([item["version"] for item in entries], ["0.2.0", "0.2.0", "0.1.0"])
        for item in entries:
            self.assertIn("mcangeli/uls-plugins", item["source"])
        self.assertNotIn("hello-world", [item["id"] for item in entries])

    def test_rejects_mismatched_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            path.write_text(json.dumps({"schema_version": 1, "plugins": [{
                "id": "swimming-fish", "name": "Fish", "description": "",
                "version": "0.1.0",
                "source": "https://github.com/mcangeli/uls-plugins/tree/main/plugins/other"
            }]}))
            with self.assertRaises(ManifestError):
                read_official_catalog(path)


    def test_dynamic_catalog_fetch_cache_and_offline_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            remote = {"schema_version": 1, "plugins": [{
                "id": "test-plugin", "name": "Test", "description": "",
                "version": "0.1.0",
                "source": "https://github.com/mcangeli/uls-plugins/tree/main/plugins/test-plugin"
            }]}
            payload = json.dumps(remote).encode("utf-8")
            entries, source = dynamic_official_catalog(cache_path=cache, fetch=lambda: payload, now=time.time())
            self.assertEqual(source, "remote")
            self.assertEqual(entries[0]["id"], "test-plugin")
            entries, source = dynamic_official_catalog(cache_path=cache, fetch=lambda: (_ for _ in ()).throw(OSError()), now=100000)
            self.assertEqual(source, "cache")
            entries, source = dynamic_official_catalog(cache_path=cache, fetch=lambda: (_ for _ in ()).throw(OSError()), now=time.time() + 100000)
            self.assertEqual(source, "stale-cache")
            entries, source = dynamic_official_catalog(cache_path=Path(tmp) / "missing.json",
                fetch=lambda: (_ for _ in ()).throw(OSError()), now=9999999999)
            self.assertEqual(source, "bundled-fallback")
            self.assertIn("daily-calendar", [entry["id"] for entry in entries])

    def test_corrupt_cache_falls_back_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            cache.write_text('{"schema_version":1,"plugins":"not-a-list"}')
            entries, source = dynamic_official_catalog(
                cache_path=cache,
                fetch=lambda: (_ for _ in ()).throw(OSError("offline")),
                refresh=True,
            )
            self.assertEqual(source, "bundled-fallback")
            self.assertTrue(entries)

    def test_rejects_invalid_remote_without_poisoning_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "cache.json"
            entries, source = dynamic_official_catalog(cache_path=cache,
                fetch=lambda: b'{"schema_version":1,"plugins":[{"id":"wrong"}]}', refresh=True)
            self.assertEqual(source, "bundled-fallback")
            self.assertFalse(cache.exists())


if __name__ == "__main__":
    unittest.main()
