"""Regression checks for dashboard update privilege boundary and UI wiring."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DashboardUpdateTests(unittest.TestCase):
    def test_update_helpers_accept_no_arguments(self):
        for name in ('uls-update-status', 'uls-update-launch', 'uls-update-worker'):
            source = (ROOT / 'scripts' / name).read_text()
            self.assertIn('$# -eq 0', source)

    def test_web_update_endpoints_require_existing_auth_boundary(self):
        source = (ROOT / 'universal_led' / 'configurator.py').read_text()
        self.assertIn("elif path=='/api/update/check':", source)
        self.assertIn("elif path=='/api/update/progress':", source)
        self.assertIn("if path=='/api/update/install':", source)
        self.assertIn("if data != {'confirm':True}:", source)
        self.assertIn("['sudo','-n','/usr/local/libexec/uls-update-launch']", source)
        self.assertIn("['sudo','-n','/usr/local/libexec/uls-update-status']", source)
        self.assertIn("'X-Configurator-Token':token", source)

    def test_install_and_upgrade_register_scoped_helper(self):
        for name in ('install-system.sh', 'uls-update'):
            source = (ROOT / 'scripts' / name).read_text()
            self.assertIn('install-dashboard-update-helper.sh', source)

    def test_emulator_update_does_not_require_matrix_service(self):
        updater = (ROOT / 'scripts' / 'uls-update').read_text()
        cli = (ROOT / 'scripts' / 'ulsctl').read_text()
        self.assertIn('list-unit-files uls-matrix.service', updater)
        self.assertIn('list-unit-files uls-matrix.service', cli)

    def test_dashboard_polls_update_progress(self):
        source = (ROOT / 'universal_led' / 'configurator.py').read_text()
        self.assertIn('setInterval(()=>', source)
        self.assertIn('refreshUpdateProgress()', source)

    def test_detached_job_survives_web_restart(self):
        source = (ROOT / 'scripts' / 'uls-update-launch').read_text()
        self.assertIn('systemd-run', source)
        self.assertIn('uls-dashboard-update', source)


if __name__ == '__main__':
    unittest.main()
