import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from universal_led.wifi_hotspot_maintenance import maintain
from universal_led.wifi_diagnostics import _split_nmcli

class HotspotMaintenanceTests(unittest.TestCase):
    def fake(self, state='disconnected', connection='--', saved='', success=False):
        calls = []
        def run(args, **kw):
            calls.append(args)
            if args[-2:] == ['device', 'status']:
                out = 'wlan0:wifi:' + state + ':' + connection + '\neth0:ethernet:connected:Wired\n'
            elif args[-2:] == ['connection', 'show']:
                out = saved
            elif '802-11-wireless.mode' in args:
                out = 'ap\n' if args[-1] == 'Universal-LED-Setup' else 'infrastructure\n'
            elif 'connection' in args and 'up' in args:
                return SimpleNamespace(returncode=0 if success else 1, stdout='')
            else:
                out = ''
            return SimpleNamespace(returncode=0, stdout=out)
        return run, calls

    def test_connected_client_untouched(self):
        run, calls = self.fake('connected', 'Home')
        self.assertEqual(maintain(run=run, pending=Path('/nonexistent')), 'client_connected')
        self.assertFalse(any('up' in a for a in calls))

    def test_active_hotspot_untouched(self):
        run, calls = self.fake('connected', 'Universal-LED-Setup')
        self.assertEqual(maintain(run=run, pending=Path('/nonexistent')), 'hotspot_active')
        self.assertFalse(any('up' in a for a in calls))

    def test_fallback_without_saved_profiles(self):
        run, calls = self.fake(success=True)
        self.assertEqual(maintain(run=run, pending=Path('/nonexistent')), 'hotspot_started')
        self.assertTrue(any('Universal-LED-Setup' in a and 'up' in a for a in calls))

    def test_rollback_blocks_network_changes(self):
        with TemporaryDirectory() as folder:
            Path(folder, 'pending.json').write_text('{}')
            run, calls = self.fake()
            self.assertEqual(maintain(run=run, pending=Path(folder)), 'rollback_pending')
            self.assertEqual(calls, [])

    def test_escaped_nmcli_fields(self):
        self.assertEqual(_split_nmcli('Home\\:Office:uuid:wifi:wlan0')[0], 'Home:Office')

if __name__ == '__main__':
    unittest.main()
