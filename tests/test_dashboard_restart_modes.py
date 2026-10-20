"""Dashboard self-restart must respect physical and emulator modes."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DashboardRestartModesTests(unittest.TestCase):
    def test_worker_checks_matrix_presence_before_applying(self):
        worker = (ROOT / "scripts/uls-restart-worker").read_text()
        self.assertIn("list-unit-files uls-matrix.service", worker)
        self.assertIn("if [ \"$matrix_present\" -eq 1 ]; then", worker)
        self.assertIn("/usr/local/libexec/uls-matrix-control apply", worker)
        self.assertNotIn("systemctl restart uls-matrix.service", worker)

    def test_restart_is_detached_from_web_service(self):
        launcher = (ROOT / "scripts/uls-restart-services").read_text()
        self.assertIn("systemd-run", launcher)
        self.assertIn("--on-active=2s", launcher)


if __name__ == "__main__":
    unittest.main()
