import json
import tempfile
import unittest
from pathlib import Path
from universal_led.official_plugin_catalog import read_official_catalog
from universal_led.plugin_manifest import ManifestError


class OfficialPluginCatalogTests(unittest.TestCase):
    def test_only_optional_plugins_are_catalogued(self):
        entries = read_official_catalog()
        self.assertEqual([item["id"] for item in entries], ["swimming-fish"])
        self.assertIn("mcangeli/uls-plugins", entries[0]["source"])
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


if __name__ == "__main__":
    unittest.main()
