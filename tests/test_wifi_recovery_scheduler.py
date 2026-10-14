import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from universal_led.wifi_recovery_scheduler import (
    arm_recovery, recovery_pending, validate_target)

TOKEN='a'*32

class RecoverySchedulerTests(unittest.TestCase):
    def test_validate_target(self):
        validate_target('wlan0','Home Wi-Fi')
        for iface,profile in [('eth0','Home'),('wlan0',''),('wlan0','bad\nname'),
                              ('wlan0','x'*129),('wlan0;rm','Home')]:
            with self.subTest(iface=iface,profile=profile),self.assertRaises(ValueError):
                validate_target(iface,profile)

    def test_nonroot_refused(self):
        with patch('universal_led.wifi_recovery_scheduler.os.geteuid',return_value=1000):
            with self.assertRaises(PermissionError):
                arm_recovery('wlan0','Home')

    def test_arming_starts_independent_unit(self):
        with tempfile.TemporaryDirectory() as temp, \
             patch('universal_led.wifi_recovery_scheduler.os.geteuid',return_value=0), \
             patch('universal_led.wifi_recovery_scheduler.Path.stat',
                   return_value=SimpleNamespace(st_uid=0)):
            state_dir=Path(temp)/'recovery'
            runner=Mock(return_value=SimpleNamespace(returncode=0))
            token=arm_recovery('wlan0','Original',state_dir=state_dir,
                               run=runner,token_factory=lambda:TOKEN)
            self.assertEqual(token,TOKEN)
            self.assertTrue(recovery_pending(TOKEN,state_dir=state_dir))
            command=runner.call_args.args[0]
            self.assertEqual(command[:4],['systemd-run','--system','--quiet','--collect'])
            self.assertIn('--unit=universal-led-wifi-recovery-'+TOKEN,command)
            self.assertEqual(command[-1],TOKEN)
            self.assertNotIn('Original',command)

    def test_scheduling_failure_cleans_up(self):
        with tempfile.TemporaryDirectory() as temp, \
             patch('universal_led.wifi_recovery_scheduler.os.geteuid',return_value=0), \
             patch('universal_led.wifi_recovery_scheduler.Path.stat',
                   return_value=SimpleNamespace(st_uid=0)):
            state_dir=Path(temp)/'recovery'
            runner=Mock(return_value=SimpleNamespace(returncode=1))
            with self.assertRaises(RuntimeError):
                arm_recovery('wlan0','Original',state_dir=state_dir,
                             run=runner,token_factory=lambda:TOKEN)
            self.assertFalse(recovery_pending(TOKEN,state_dir=state_dir))

    def test_invalid_token_not_pending(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertFalse(recovery_pending('../etc/passwd',state_dir=Path(temp)))

if __name__=='__main__':
    unittest.main()
