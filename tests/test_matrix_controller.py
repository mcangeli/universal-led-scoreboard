"""Safety checks for the privileged matrix controller."""
import subprocess
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "uls-matrix-control"


class MatrixControllerTests(unittest.TestCase):
    def test_shell_syntax(self):
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)

    def test_helper_limits_service_scope(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("UNIT=uls-matrix.service", script)
        self.assertIn('systemctl restart "$UNIT"', script)
        self.assertIn('systemctl stop "$UNIT"', script)
        self.assertNotIn("uls-web.service", script)

    def test_last_good_snapshot_and_rollback(self):
        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("matrix.applied.json", script)
        self.assertIn('cp "$GOOD" "$CONFIG"', script)
        self.assertIn('cp "$CONFIG" "$GOOD"', script)
        self.assertIn("sleep 3", script)


if __name__ == "__main__":
    unittest.main()
