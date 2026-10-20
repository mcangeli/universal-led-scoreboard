"""GitHub plugin review does not execute untrusted code."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led.plugin_review import inspect_github_plugin
from universal_led.plugin_manifest import ManifestError


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class PluginReviewTests(unittest.TestCase):
    def test_rejects_non_github_source_without_network(self):
        with patch("urllib.request.urlopen") as request:
            with self.assertRaises(ManifestError):
                inspect_github_plugin("http://example.com/plugin")
            request.assert_not_called()

    def test_reviews_pinned_manifest(self):
        commit = "a" * 40

        def download(source, sha, target):
            self.assertEqual(sha, commit)
            target.mkdir()
            (target / "uls-plugin.json").write_text(json.dumps({
                "id": "sample", "name": "Sample", "version": "1.0.0",
                "api_version": 1, "capabilities": ["screen"],
                "entry_point": "sample:Screen",
            }))
            return target

        with patch("urllib.request.urlopen", return_value=Response(json.dumps({"sha": commit}).encode())), patch(
            "universal_led.plugin_review.download_github_plugin", side_effect=download
        ):
            result = inspect_github_plugin("https://github.com/owner/repo")
        self.assertEqual(result["commit"], commit)
        self.assertEqual(result["id"], "sample")
        self.assertFalse(result["enabled"])

    def test_rejects_invalid_manifest(self):
        def download(source, sha, target):
            target.mkdir()
            (target / "uls-plugin.json").write_text('{"id":"invalid"}')
            return target

        with patch("urllib.request.urlopen", return_value=Response(json.dumps({"sha": "b" * 40}).encode())), patch(
            "universal_led.plugin_review.download_github_plugin", side_effect=download
        ):
            with self.assertRaises(ManifestError):
                inspect_github_plugin("https://github.com/owner/repo")

    def test_rejects_oversized_commit_response(self):
        with patch("urllib.request.urlopen", return_value=Response(b"x" * (1024 * 1024 + 1))):
            with self.assertRaises(ValueError):
                inspect_github_plugin("https://github.com/owner/repo")


if __name__ == "__main__":
    unittest.main()
