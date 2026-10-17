"""Dashboard branch switching safeguards."""
import subprocess
import unittest
from pathlib import Path
from universal_led.configurator import HTML

ROOT = Path(__file__).resolve().parents[1]


class DashboardBranchUpdateTests(unittest.TestCase):
    def test_shell_scripts_parse(self):
        for name in ("uls-update", "uls-update-status", "install-dashboard-update-helper.sh"):
            with self.subTest(name=name):
                subprocess.run(["bash", "-n", str(ROOT / "scripts" / name)], check=True)

    def test_branch_picker_and_confirmation(self):
        self.assertIn('id="update-branch"', HTML)
        self.assertIn('branch:document.getElementById', HTML)
        self.assertIn('Candidate tests will run', HTML)

    def test_branch_filter_keeps_full_list_available(self):
        self.assertIn('id="update-show-all"', HTML)
        self.assertIn('function renderUpdateBranches()', HTML)
        self.assertIn('showAll?branches:relevant', HTML)
        self.assertIn("name===data.branch||name==='main'", HTML)

    def test_update_checks_candidate_before_switch(self):
        script = (ROOT / "scripts" / "uls-update").read_text()
        self.assertLess(script.index("Checking candidate code"), script.index('as_owner git checkout -B "$BRANCH" "$NEW"'))
        self.assertIn('OLD_BRANCH="$BRANCH"', script)
        self.assertIn('as_owner git checkout -f "$OLD_BRANCH"', script)

    def test_fetch_precedes_fast_forward_validation(self):
        script = (ROOT / "scripts" / "uls-update").read_text()
        self.assertLess(script.index('as_owner git fetch "$REMOTE" "$BRANCH"'), script.index('as_owner git merge-base --is-ancestor'))
        self.assertIn('as_owner git rev-parse FETCH_HEAD', script)

    def test_branch_request_cleared_on_early_failure(self):
        script = (ROOT / "scripts" / "uls-update").read_text()
        self.assertLess(script.index("trap 'rm -f"), script.index("as_owner git ls-remote"))
        self.assertIn('cleanup; rm -f "$REQUEST"', script)

    def test_privileged_selector_limits_input(self):
        script = (ROOT / "scripts" / "uls-update-select").read_text()
        compile(script, "uls-update-select", "exec")
        self.assertIn('re.fullmatch', script)
        self.assertIn('os.replace', script)


if __name__ == "__main__":
    unittest.main()
