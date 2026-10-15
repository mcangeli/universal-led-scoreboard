import subprocess
import unittest
from types import SimpleNamespace
from universal_led.wifi_saved_profiles import saved_wifi_profiles


class SavedWifiProfilesTests(unittest.TestCase):
    def test_saved_and_active_profiles(self):
        output = ('Home\\:Office:11111111-1111-1111-1111-111111111111:802-11-wireless:wlan0\n'
                  'Guest:22222222-2222-2222-2222-222222222222:wifi:--\n'
                  'Ethernet:33333333-3333-3333-3333-333333333333:802-3-ethernet:eth0\n')
        result = saved_wifi_profiles(run=lambda *a, **kw: SimpleNamespace(returncode=0, stdout=output))
        self.assertTrue(result['available'])
        self.assertEqual([p['name'] for p in result['profiles']], ['Home:Office', 'Guest'])
        self.assertEqual([p['active'] for p in result['profiles']], [True, False])
        self.assertEqual(result['profiles'][1]['interface'], '')

    def test_no_password_commands(self):
        seen = []
        def run(args, **kw):
            seen.extend(args)
            return SimpleNamespace(returncode=0, stdout='')
        saved_wifi_profiles(run=run)
        self.assertNotIn('secrets', seen)
        self.assertNotIn('password', seen)
        self.assertEqual(seen[-2:], ['connection', 'show'])

    def test_nmcli_failure(self):
        result = saved_wifi_profiles(run=lambda *a, **kw: SimpleNamespace(returncode=1, stdout=''))
        self.assertFalse(result['available'])
        self.assertEqual(result['profiles'], [])

    def test_missing_nmcli(self):
        def missing(*a, **kw):
            raise FileNotFoundError()
        self.assertFalse(saved_wifi_profiles(run=missing)['available'])

    def test_timeout(self):
        def timeout(*a, **kw):
            raise subprocess.TimeoutExpired('nmcli', 8)
        self.assertFalse(saved_wifi_profiles(run=timeout)['available'])

    def test_malformed_rows_skipped(self):
        result = saved_wifi_profiles(run=lambda *a, **kw: SimpleNamespace(
            returncode=0, stdout='bad-row\nNoUUID::wifi:wlan0\n'))
        self.assertEqual(result['profiles'], [])


if __name__ == '__main__':
    unittest.main()
