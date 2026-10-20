"""Guard updater rollback helper parity without modifying system services."""
from pathlib import Path
import unittest

UPDATER = (Path(__file__).resolve().parents[1] / "scripts" / "uls-update").read_text()


class UpdateRollbackHelpersTests(unittest.TestCase):
    def test_rollback_reinstalls_all_privilege_helpers(self):
        rollback = UPDATER.split("rollback() {", 1)[1].split("\ntrap rollback ERR", 1)[0]
        install = UPDATER.split("\ntrap rollback ERR", 1)[1]
        helpers = (
            "install-dashboard-update-helper.sh",
            "install-dashboard-restart-helper.sh",
            "install-wifi-scan-helper.sh",
            "install-wifi-control-helper.sh",
        )
        for helper in helpers:
            with self.subTest(helper=helper):
                self.assertIn(helper, rollback)
                self.assertIn(helper, install)

    def test_rollback_does_not_reprovision_hotspot(self):
        rollback = UPDATER.split("rollback() {", 1)[1].split("\ntrap rollback ERR", 1)[0]
        self.assertNotIn("provision-hotspot.sh", rollback)

    def test_rollback_restores_git_before_helpers(self):
        rollback = UPDATER.split("rollback() {", 1)[1].split("\ntrap rollback ERR", 1)[0]
        self.assertLess(rollback.index('git reset --hard "$OLD"'), rollback.index('install-dashboard-update-helper.sh'))


if __name__ == "__main__":
    unittest.main()
