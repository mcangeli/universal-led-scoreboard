import unittest
from unittest.mock import patch
from types import SimpleNamespace
import subprocess
from universal_led.wifi_switch_saved import switch_saved_profile

UUID = '11111111-1111-1111-1111-111111111111'


class SavedWifiSwitchTests(unittest.TestCase):
    def invoke(self, **overrides):
        calls = []
        def arm(*args):
            calls.append(('arm', args))
            return 'a' * 32
        def run(args, **kwargs):
            calls.append(('run', args))
            return SimpleNamespace(returncode=overrides.get('returncode', 0))
        with patch('universal_led.wifi_switch_saved.os.geteuid', return_value=0):
            result = switch_saved_profile('wlan0', 'Old Network', 'New Network', UUID,
                                          arm=overrides.get('arm', arm),
                                          run=overrides.get('run', run))
        return result, calls

    def test_rollback_armed_before_network_change(self):
        result, calls = self.invoke()
        self.assertEqual([c[0] for c in calls], ['arm', 'run'])
        self.assertTrue(result['started'])
        self.assertTrue(result['confirmation_required'])
        self.assertIn('uuid', calls[1][1])

    def test_connection_failure_keeps_rollback_armed(self):
        result, calls = self.invoke(returncode=10)
        self.assertFalse(result['started'])
        self.assertEqual(result['recovery_token'], 'a' * 32)

    def test_timeout_keeps_rollback_armed(self):
        def timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired('nmcli', 55)
        result, calls = self.invoke(run=timeout)
        self.assertFalse(result['started'])
        self.assertEqual(calls[0][0], 'arm')

    def test_arm_failure_prevents_connection_attempt(self):
        def fail(*args):
            raise RuntimeError('recovery unavailable')
        with self.assertRaises(RuntimeError):
            self.invoke(arm=fail)

    def test_bad_uuid_rejected(self):
        with patch('universal_led.wifi_switch_saved.os.geteuid', return_value=0):
            with self.assertRaises(ValueError):
                switch_saved_profile('wlan0', 'Old', 'New', 'not-a-uuid')

    def test_non_root_rejected(self):
        with patch('universal_led.wifi_switch_saved.os.geteuid', return_value=1000):
            with self.assertRaises(PermissionError):
                switch_saved_profile('wlan0', 'Old', 'New', UUID)


if __name__ == '__main__':
    unittest.main()
