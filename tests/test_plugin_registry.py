"""Plugin source and installed-registry validation tests."""
import json
import tempfile
import unittest
from pathlib import Path

from universal_led.plugin_manifest import ManifestError
from universal_led.plugin_registry import parse_github_source, registry_record, read_registry


MANIFEST = {
    "id": "test-screen", "name": "Test Screen", "version": "1.0.0",
    "api_version": 1, "capabilities": ["screen"], "entry_point": "plugin:Plugin",
}
SHA = "a" * 40


class PluginRegistryTests(unittest.TestCase):
    def test_canonical_github_sources(self):
        self.assertEqual(parse_github_source("https://github.com/owner/repo.git"),
                         ("owner", "repo"))
        self.assertEqual(parse_github_source("https://github.com/owner/repo/"),
                         ("owner", "repo"))

    def test_reject_untrusted_source_forms(self):
        for source in (
            "http://github.com/owner/repo",
            "https://evil.example/owner/repo",
            "https://github.com.evil.example/owner/repo",
            "https://github.com/owner/repo/tree/main",
            "https://github.com/owner/repo?ref=main",
            "https://user:pass@github.com/owner/repo",
            "https://github.com/owner/../repo",
        ):
            with self.subTest(source=source), self.assertRaises(ManifestError):
                parse_github_source(source)

    def test_registry_record_requires_immutable_commit(self):
        record = registry_record(MANIFEST, "https://github.com/owner/repo", SHA)
        self.assertEqual(record["id"], "test-screen")
        self.assertFalse(record["enabled"])
        with self.assertRaises(ManifestError):
            registry_record(MANIFEST, "https://github.com/owner/repo", "main")

    def test_registry_read_and_invalid_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "installed.json"
            self.assertEqual(read_registry(path), {})
            record = registry_record(MANIFEST, "https://github.com/owner/repo", SHA)
            path.write_text(json.dumps({"test-screen": record}))
            self.assertEqual(read_registry(path)["test-screen"], record)
            path.write_text(json.dumps({"different-id": record}))
            with self.assertRaises(ManifestError):
                read_registry(path)


if __name__ == "__main__":
    unittest.main()
