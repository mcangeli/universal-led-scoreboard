"""Release-candidate identity and backward-compatible settings smoke tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led import __version__
from universal_led.release import PREVIEW, display_version
from universal_led.sport_settings import load_settings


class ReleaseCandidateTests(unittest.TestCase):
    def test_preview_identity_matches_package_version(self):
        self.assertEqual(PREVIEW, "0.6.0")
        self.assertEqual(__version__, "0.6.0.dev0")

    def test_dashboard_identity_includes_commit_when_available(self):
        with patch("universal_led.release.installed_commit", return_value="abc12345"):
            self.assertEqual(display_version(), "v0.6.0.dev0 · abc12345")

    def test_dashboard_identity_works_without_git(self):
        with patch("universal_led.release.installed_commit", return_value=None):
            self.assertEqual(display_version(), "v0.6.0.dev0")

    def test_new_install_english_disabled_without_creating_settings_file(self):
        with tempfile.TemporaryDirectory() as root:
            settings = load_settings(root)
            self.assertFalse(settings["sports"]["english"]["enabled"])
            self.assertFalse(Path(root, "settings.json").exists())


if __name__ == "__main__":
    unittest.main()
