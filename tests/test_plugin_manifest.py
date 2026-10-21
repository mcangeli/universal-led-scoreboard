"""Tests for metadata-only plugin discovery."""
import json
import tempfile
import unittest
from pathlib import Path

from universal_led.plugin_manifest import ManifestError, discover_plugins, parse_manifest


def valid(**changes):
    data = {"id": "sample", "name": "Sample screen", "version": "0.1.0",
            "api_version": 1, "capabilities": ["screen"],
            "entry_point": "sample.screen:register"}
    data.update(changes)
    return data


class PluginManifestTests(unittest.TestCase):
    def test_valid_manifest(self):
        manifest = parse_manifest(valid())
        self.assertEqual(manifest.plugin_id, "sample")
        self.assertEqual(manifest.capabilities, ("screen",))

    def test_rejects_incompatible_api(self):
        with self.assertRaises(ManifestError):
            parse_manifest(valid(api_version=2))
        with self.assertRaises(ManifestError):
            parse_manifest(valid(api_version=True))

    def test_rejects_unsafe_ids_and_entry_points(self):
        for bad in ("../evil", "a/b", "A", ".hidden"):
            with self.subTest(bad=bad), self.assertRaises(ManifestError):
                parse_manifest(valid(id=bad))
        for bad in ("os:system()", "../../evil:load", "module", "a:b;c"):
            with self.subTest(bad=bad), self.assertRaises(ManifestError):
                parse_manifest(valid(entry_point=bad))

    def test_rejects_invalid_capabilities_and_unknown_fields(self):
        for capabilities in ([], ["screen", "screen"], ["root"], "screen"):
            with self.subTest(capabilities=capabilities), self.assertRaises(ManifestError):
                parse_manifest(valid(capabilities=capabilities))
        with self.assertRaises(ManifestError):
            parse_manifest(valid(surprise=True))

    def test_discovery_keeps_valid_plugins_when_another_is_broken(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            good = root / "sample"
            good.mkdir()
            (good / "uls-plugin.json").write_text(json.dumps(valid()))
            bad = root / "broken"
            bad.mkdir()
            (bad / "uls-plugin.json").write_text("{bad json")
            found, errors = discover_plugins(root)
            self.assertEqual(list(found), ["sample"])
            self.assertIn("broken", errors)

    def test_mismatched_folder_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "other"
            folder.mkdir()
            (folder / "uls-plugin.json").write_text(json.dumps(valid()))
            found, errors = discover_plugins(temp)
            self.assertFalse(found)
            self.assertIn("other", errors)

    def test_symlinks_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            outside = root / "outside"
            outside.mkdir()
            (outside / "uls-plugin.json").write_text(json.dumps(valid(id="outside")))
            (root / "linked").symlink_to(outside, target_is_directory=True)
            found, errors = discover_plugins(root)
            self.assertEqual(set(found), {"outside"})
            self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()
