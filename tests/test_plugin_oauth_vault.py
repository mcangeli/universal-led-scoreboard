"""Offline tests for Core OAuth vault permission and isolation rules."""
import tempfile
from pathlib import Path
import unittest

from universal_led.plugin_oauth_vault import PluginTokenVault, VaultError


class VaultTests(unittest.TestCase):
    def test_roundtrip_permissions_and_delete(self):
        with tempfile.TemporaryDirectory() as root:
            vault = PluginTokenVault(Path(root) / "private")
            vault.save("daily-calendar", {"refresh_token": "secret", "access_token": "short"})
            self.assertEqual((Path(root) / "private").stat().st_mode & 0o777, 0o700)
            self.assertEqual((Path(root) / "private" / "daily-calendar.json").stat().st_mode & 0o777, 0o600)
            self.assertEqual(vault.load("daily-calendar")["refresh_token"], "secret")
            vault.delete("daily-calendar")
            with self.assertRaises(VaultError):
                vault.load("daily-calendar")

    def test_reject_traversal_and_symlink(self):
        with tempfile.TemporaryDirectory() as root:
            vault = PluginTokenVault(Path(root) / "private")
            with self.assertRaises(VaultError):
                vault.save("../escape", {"refresh_token": "secret"})
            target = Path(root) / "target"
            target.write_text("untouched")
            (Path(root) / "private").mkdir(mode=0o700)
            (Path(root) / "private" / "daily-calendar.json").symlink_to(target)
            with self.assertRaises(VaultError):
                vault.save("daily-calendar", {"refresh_token": "secret"})
            self.assertEqual(target.read_text(), "untouched")

    def test_refuse_world_readable_vault(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "private"
            path.mkdir(mode=0o755)
            with self.assertRaises(VaultError):
                PluginTokenVault(path).save("daily-calendar", {"refresh_token": "secret"})


if __name__ == "__main__":
    unittest.main()
