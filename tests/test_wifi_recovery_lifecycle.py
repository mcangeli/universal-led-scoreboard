import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from universal_led.wifi_recovery_lifecycle import (
    unit_name, inspect_recovery_unit, require_running_recovery)

TOKEN='a'*32

class RecoveryLifecycleTests(unittest.TestCase):
    def runner(self, output, code=0):
        return Mock(return_value=SimpleNamespace(stdout=output,returncode=code))

    def test_unit_name_is_fixed_and_validated(self):
        self.assertEqual(unit_name(TOKEN),'universal-led-wifi-recovery-'+TOKEN+'.service')
        for invalid in ('','a'*31,'A'*32,'a'*32+';id',None):
            with self.subTest(token=invalid),self.assertRaises(ValueError):
                unit_name(invalid)

    def test_running_unit_accepted(self):
        run=self.runner('LoadState=loaded\nActiveState=active\nSubState=running\nResult=success\n')
        self.assertTrue(inspect_recovery_unit(TOKEN,run=run)['armed'])
        self.assertEqual(run.call_args.args[0][:3],
                         ['systemctl','--system','show'])

    def test_inactive_unit_rejected(self):
        run=self.runner('LoadState=loaded\nActiveState=inactive\nSubState=dead\nResult=success\n')
        self.assertFalse(inspect_recovery_unit(TOKEN,run=run)['armed'])

    def test_failed_unit_rejected(self):
        run=self.runner('LoadState=loaded\nActiveState=failed\nSubState=failed\nResult=exit-code\n')
        self.assertFalse(inspect_recovery_unit(TOKEN,run=run)['armed'])

    def test_missing_unit_rejected(self):
        self.assertFalse(inspect_recovery_unit(TOKEN,run=self.runner('',1))['armed'])

    def test_incomplete_response_rejected(self):
        self.assertFalse(inspect_recovery_unit(TOKEN,run=self.runner('ActiveState=active\n'))['armed'])

    def test_systemctl_timeout_rejected(self):
        def timeout(*a,**kw):
            raise subprocess.TimeoutExpired('systemctl',8)
        self.assertFalse(inspect_recovery_unit(TOKEN,run=timeout)['armed'])

    def test_require_running_fails_closed(self):
        with self.assertRaises(RuntimeError):
            require_running_recovery(TOKEN,run=self.runner('ActiveState=inactive\n'))

    def test_require_running_succeeds(self):
        self.assertTrue(require_running_recovery(
            TOKEN,run=self.runner('LoadState=loaded\nActiveState=active\nSubState=running\nResult=success\n')))

if __name__=='__main__':
    unittest.main()
