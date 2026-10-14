import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from universal_led.wifi_recovery import run_privileged_recovery, verify_privileged_state

TOKEN='f'*32

class PrivilegedRecoverySecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'state'
        self.directory.mkdir(mode=0o700)
        self.path=self.directory/(TOKEN+'.json')
        self.path.write_text('{}',encoding='utf-8')
        self.path.chmod(0o600)

    def test_standalone_validator_accepts_private_file(self):
        self.assertTrue(verify_privileged_state(
            TOKEN,state_dir=self.directory,expected_uid=os.getuid()))

    def test_standalone_validator_rejects_insecure_file(self):
        self.path.chmod(0o644)
        self.assertFalse(verify_privileged_state(
            TOKEN,state_dir=self.directory,expected_uid=os.getuid()))

    def test_privileged_entrypoint_denies_bad_state(self):
        worker=Mock()
        with patch('universal_led.wifi_recovery.os.geteuid',return_value=0):
            with self.assertRaises(PermissionError):
                run_privileged_recovery(TOKEN,state_dir=self.directory,
                                        verify=lambda *a,**k:False,worker=worker)
        worker.assert_not_called()

    def test_privileged_entrypoint_runs_after_verification(self):
        worker=Mock(return_value=True)
        with patch('universal_led.wifi_recovery.os.geteuid',return_value=0):
            result=run_privileged_recovery(
                TOKEN,state_dir=self.directory,
                verify=lambda *a,**k:True,worker=worker)
        self.assertTrue(result)
        worker.assert_called_once_with(TOKEN,state_dir=self.directory)

    def test_privileged_entrypoint_denies_nonroot(self):
        worker=Mock()
        with patch('universal_led.wifi_recovery.os.geteuid',return_value=1000):
            with self.assertRaises(PermissionError):
                run_privileged_recovery(TOKEN,state_dir=self.directory,
                                        verify=lambda *a,**k:True,worker=worker)
        worker.assert_not_called()

if __name__=='__main__':
    unittest.main()
