import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INSTALLER=ROOT/'scripts'/'install-wifi-connect-helper.sh'
HELPER=ROOT/'scripts'/'universal-led-wifi-connect'

class WifiHelperInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script=INSTALLER.read_text()
        cls.helper=HELPER.read_text()

    def test_installer_uses_strict_shell_and_root(self):
        self.assertIn('set -euo pipefail',self.script)
        self.assertIn('if [[ "$EUID" -ne 0 ]]',self.script)
        self.assertIn('SUDO_USER',self.script)

    def test_helper_is_preflight_only(self):
        self.assertIn("request['operation'] != 'preflight'",self.helper)
        self.assertIn("'switching_enabled':False",self.helper)

    def test_installer_restricts_sudo_to_exact_no_args(self):
        self.assertIn('NOPASSWD: %s ""',self.script)
        self.assertIn('visudo -cf',self.script)
        self.assertNotIn('NOPASSWD: ALL',self.script)

    def test_installer_does_not_change_wifi(self):
        for forbidden in ('nmcli connection up','nmcli device disconnect',
                          'systemd-run','systemctl start','nmcli connection modify'):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,self.script)

    def test_recovery_worker_installed_but_not_armed(self):
        self.assertIn('wifi_recovery.py',self.script)
        self.assertIn('universal-led-wifi-recovery',self.script)
        self.assertNotIn('arm_recovery(',self.script)

if __name__=='__main__':
    unittest.main()
