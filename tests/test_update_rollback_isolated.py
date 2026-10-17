"""Exercise the production rollback function with isolated command stubs.

No Git checkout, system service, matrix, or system configuration is modified.
"""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IsolatedRollbackTests(unittest.TestCase):
    def test_post_checkout_failure_restores_code_and_helpers(self):
        script = (ROOT / "scripts" / "uls-update").read_text()
        function = "rollback() {" + script.split("rollback() {", 1)[1].split("\ntrap rollback ERR", 1)[0]
        # Run the actual rollback function, but replace every external side effect.
        harness = r"""
set -Eeuo pipefail
OLD=previous-commit
OLD_BRANCH=feature/0.4.5-dashboard-polish
APP=/isolated/uls
REQUEST=/isolated/branch-request
STAGE=/isolated/stage
as_owner() {
  case "$*" in
    "git branch --show-current") echo other-branch ;;
    "git checkout -f "*|"git reset --hard "*) printf '%s\n' "$*" ;;
    *) return 98 ;;
  esac
}
rm() { printf 'rm %s\n' "$*"; }
install() { printf 'install %s\n' "$*"; }
bash() { printf 'bash %s\n' "$*"; }
systemctl() {
  case "$*" in
    "list-unit-files uls-matrix.service --no-legend") echo uls-matrix.service ;;
    *) printf 'systemctl %s\n' "$*" ;;
  esac
}
grep() { command grep "$@"; }
"""
        command = harness + "\n" + function + "\ntrap rollback ERR\nfalse\n"
        result = subprocess.run(
            ["bash", "-c", command], text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        combined = result.stdout + result.stderr
        for expected in (
            "git checkout -f feature/0.4.5-dashboard-polish",
            "git reset --hard previous-commit",
            "install-dashboard-update-helper.sh",
            "install-dashboard-restart-helper.sh",
            "systemctl restart uls-web.service",
            "uls-matrix-control apply",
            "Rollback attempted",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, combined)


if __name__ == "__main__":
    unittest.main()
