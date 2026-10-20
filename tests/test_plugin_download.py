"""Tests for GitHub plugin archive extraction boundaries."""
import io
import tarfile
import tempfile
import unittest
from pathlib import Path

from universal_led.plugin_download import extract_github_archive
from universal_led.plugin_manifest import ManifestError


def archive_with(name, payload=b"data", kind=tarfile.REGTYPE):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        info = tarfile.TarInfo(name)
        info.type = kind
        info.size = len(payload) if kind == tarfile.REGTYPE else 0
        tar.addfile(info, io.BytesIO(payload) if info.size else None)
    return buffer.getvalue()


class GitHubArchiveTests(unittest.TestCase):
    def test_extract_strips_single_archive_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "package"
            result = extract_github_archive(
                archive_with("owner-repo-commit/uls-plugin.json", b"{}"), dest)
            self.assertEqual(result, dest)
            self.assertEqual((dest / "uls-plugin.json").read_bytes(), b"{}")

    def test_reject_parent_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ManifestError):
                extract_github_archive(
                    archive_with("root/../../escape.txt"), Path(tmp) / "package")
            self.assertFalse((Path(tmp) / "escape.txt").exists())

    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ManifestError):
                extract_github_archive(
                    archive_with("root/link", kind=tarfile.SYMTYPE),
                    Path(tmp) / "package")

    def test_reject_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ManifestError):
                extract_github_archive(
                    archive_with("root/uls-plugin.json"), Path(tmp))


if __name__ == "__main__":
    unittest.main()
