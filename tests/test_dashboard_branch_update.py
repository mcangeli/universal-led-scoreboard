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

    def test_installer_defaults_to_main_and_applies_matrix_config(self):
        script = (ROOT / "scripts" / "install-system.sh").read_text()
        self.assertIn("BRANCH=main", script)
        self.assertIn('sudo bash "$APP/scripts/uls-matrix-control" apply', script)

    def test_rollback_restores_privileged_helpers(self):
        script = (ROOT / "scripts" / "uls-update").read_text()
        rollback = script.split("rollback() {", 1)[1].split("trap rollback ERR", 1)[0]
        self.assertIn('install-dashboard-update-helper.sh', rollback)
        self.assertIn('install-dashboard-restart-helper.sh', rollback)

    def test_cross_branch_downgrade_rejected_before_checkout(self):
        script = (ROOT / "scripts" / "uls-update").read_text()
        self.assertLess(script.index('as_owner git merge-base --is-ancestor'), script.index('as_owner git checkout -B "$BRANCH" "$NEW"'))
        self.assertIn("unsafe branch switch/downgrade refused", script)
        self.assertIn("Candidate missing required update/matrix component", script)

    def test_fresh_install_credentials_can_write_secrets(self):
        script = (ROOT / "scripts" / "install-system.sh").read_text()
        self.assertLess(
            script.index('sudo chown "$USER:$(id -gn)" "$CONFIG/secrets"'),
            script.index('--set-admin-password'),
        )
        self.assertLess(
            script.index('--set-admin-password'),
            script.index('sudo chown -R uls:uls "$CONFIG" "$DATA"'),
        )
        self.assertIn('"$BRANCH" != *..*', script)

    def test_fresh_install_has_network_manager_dependency(self):
        script = (ROOT / "scripts" / "install-system.sh").read_text()
        self.assertIn("build-essential sudo network-manager", script)
        self.assertLess(script.index("sudo apt-get install -y git"), script.index('sudo bash "$APP/scripts/provision-hotspot.sh"'))

    def test_privileged_selector_limits_input(self):
        script = (ROOT / "scripts" / "uls-update-select").read_text()
        compile(script, "uls-update-select", "exec")
        self.assertIn('re.fullmatch', script)
        self.assertIn('os.replace', script)


if __name__ == "__main__":
    unittest.main()
