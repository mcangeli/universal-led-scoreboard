"""GitHub plugin catalog subdirectory source regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led.plugin_manifest import ManifestError
from universal_led.plugin_source import parse_plugin_source
from universal_led.plugin_registry import registry_record, read_registry
from universal_led.plugin_github_install import install_reviewed_github_plugin

SOURCE = "https://github.com/mcangeli/universal-led-scoreboard/tree/main/plugins/hello-world"
SHA = "a" * 40
MANIFEST = {
    "id": "hello-world", "name": "Hello World", "version": "1.0.0",
    "api_version": 1, "capabilities": ["screen"], "entry_point": "hello_world:Plugin",
}


class SubdirectorySourceTests(unittest.TestCase):
    def test_parse_source(self):
        self.assertEqual(parse_plugin_source(SOURCE), (
            "https://github.com/mcangeli/universal-led-scoreboard", "plugins/hello-world"))

    def test_branch_with_slashes(self):
        source = ("https://github.com/mcangeli/universal-led-scoreboard/tree/"
                  "feature/0.9.0-dynamic-team-registry/plugins/hello-world")
        self.assertEqual(parse_plugin_source(source), (
            "https://github.com/mcangeli/universal-led-scoreboard", "plugins/hello-world"))

    def test_reject_traversal_and_unexpected_paths(self):
        for source in (
            SOURCE.replace("hello-world", ".."),
            SOURCE.replace("/plugins/", "/other/"),
            SOURCE.replace("github.com", "github.com.evil.test"),
            SOURCE + "?ref=main",
            SOURCE.replace("/tree/main/", "/tree/../"),
        ):
            with self.subTest(source=source), self.assertRaises(ManifestError):
                parse_plugin_source(source)

    def test_registry_roundtrip_retains_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plugins.json"
            record = registry_record(MANIFEST, SOURCE, SHA)
            self.assertEqual(record["source"], SOURCE)
            path.write_text(json.dumps({"hello-world": record}))
            self.assertEqual(read_registry(path)["hello-world"]["source"], SOURCE)

    def test_installer_extracts_only_selected_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugins"
            root.mkdir()
            registry = Path(tmp) / "plugins.json"

            def download(source, commit, target):
                self.assertEqual(source, "https://github.com/mcangeli/universal-led-scoreboard")
                self.assertEqual(commit, SHA)
                package = target / "plugins" / "hello-world"
                package.mkdir(parents=True)
                (package / "uls-plugin.json").write_text(json.dumps(MANIFEST))
                (package / "hello_world.py").write_text("class Plugin: pass\n")
                (target / "unrelated.txt").write_text("not installed")
                return target

            with patch("universal_led.plugin_github_install.download_github_plugin", side_effect=download):
                result = install_reviewed_github_plugin(SOURCE, SHA, "hello-world", root, registry)
            self.assertEqual(result["source"], SOURCE)
            self.assertFalse(result["enabled"])
            self.assertTrue((root / "hello-world" / "hello_world.py").exists())
            self.assertFalse((root / "hello-world" / "unrelated.txt").exists())

    def test_reviewed_identity_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugins"
            root.mkdir()
            def download(source, commit, target):
                package = target / "plugins" / "hello-world"
                package.mkdir(parents=True)
                (package / "uls-plugin.json").write_text(json.dumps(MANIFEST))
                return target
            with patch("universal_led.plugin_github_install.download_github_plugin", side_effect=download):
                with self.assertRaises(ManifestError):
                    install_reviewed_github_plugin(SOURCE, SHA, "wrong-id", root, Path(tmp) / "plugins.json")
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
