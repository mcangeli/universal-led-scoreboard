"""Regression checks for disabled-matrix health and update behavior."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MatrixLifecycleScriptTests(unittest.TestCase):
    def test_script_syntax(self):
        for name in ("ulsctl", "uls-update", "uls-matrix-control"):
            with self.subTest(name=name):
                subprocess.run(["bash", "-n", str(ROOT / "scripts" / name)], check=True)

    def test_health_allows_intentionally_disabled_matrix(self):
        script = (ROOT / "scripts" / "ulsctl").read_text()
        self.assertIn("Physical matrix intentionally disabled (healthy)", script)
        self.assertIn("Matrix is running despite disabled configuration", script)

    def test_updater_follows_installed_branch(self):
        script = (ROOT / "scripts" / "uls-update").read_text()
        self.assertIn('BRANCH=$(as_owner git branch --show-current)', script)
        self.assertNotIn("BRANCH=feature/0.1.0-core-foundation", script)

    def test_updater_uses_matrix_controller(self):
        script = (ROOT / "scripts" / "uls-update").read_text()
        self.assertIn('bash "$APP/scripts/uls-matrix-control" apply', script)
        self.assertIn('bash "$APP/scripts/install-dashboard-restart-helper.sh"', script)
        self.assertNotIn("systemctl restart uls-matrix.service", script)


if __name__ == "__main__":
    unittest.main()
