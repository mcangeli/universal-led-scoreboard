import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from universal_led.wifi_switch_reservations import reserve_switch, resolve_switch

TOKEN = 'a' * 32
OTHER = 'b' * 32


class SwitchReservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'switches'
        self.directory.mkdir(mode=0o700)
        self.uid = os.geteuid()
        self.root_patch = patch('universal_led.wifi_switch_reservations.os.geteuid', return_value=0)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        if self.uid != 0:
            self.skipTest('Root-owned state test requires root; no ownership spoofing')

    def reserve(self, token=TOKEN, interface='wlan0'):
        return reserve_switch(interface, 'Home', token, directory=self.directory)

    def test_reservation_persists(self):
        self.reserve()
        self.assertEqual(json.loads((self.directory / (TOKEN + '.json')).read_text())['phase'], 'pending')

    def test_duplicate_interface_rejected(self):
        self.reserve()
        with self.assertRaises(ValueError):
            self.reserve(OTHER)

    def test_duplicate_token_rejected(self):
        self.reserve()
        with self.assertRaises(ValueError):
            self.reserve(TOKEN, 'wlan1')

    def test_distinct_interfaces_allowed(self):
        self.reserve()
        self.reserve(OTHER, 'wlan1')

    def test_confirm_frees_interface(self):
        self.reserve()
        resolve_switch(TOKEN, 'confirmed', directory=self.directory)
        self.reserve(OTHER)

    def test_expired_still_blocks(self):
        self.reserve()
        resolve_switch(TOKEN, 'expired', directory=self.directory)
        with self.assertRaises(ValueError):
            self.reserve(OTHER)

    def test_expired_cannot_confirm(self):
        self.reserve()
        resolve_switch(TOKEN, 'expired', directory=self.directory)
        with self.assertRaises(ValueError):
            resolve_switch(TOKEN, 'confirmed', directory=self.directory)

    def test_rollback_frees_interface(self):
        self.reserve()
        resolve_switch(TOKEN, 'rolled_back', directory=self.directory)
        self.reserve(OTHER)

    def test_unknown_token_rejected(self):
        with self.assertRaises(ValueError):
            resolve_switch(TOKEN, 'confirmed', directory=self.directory)

    def test_unexpected_file_fails_closed(self):
        (self.directory / 'unexpected').write_text('bad')
        with self.assertRaises(ValueError):
            self.reserve()

    def test_symlink_directory_rejected(self):
        alias = Path(self.temp.name) / 'alias'
        alias.symlink_to(self.directory, target_is_directory=True)
        with self.assertRaises(PermissionError):
            reserve_switch('wlan0', 'Home', TOKEN, directory=alias)

    def test_interrupted_creation_removes_partial_state(self):
        with patch('universal_led.wifi_switch_reservations.json.dump',
                   side_effect=OSError('interrupted write')):
            with self.assertRaises(OSError):
                self.reserve()
        self.assertFalse((self.directory / (TOKEN + '.json')).exists())
        self.reserve()

    def test_directory_sync_failure_removes_new_reservation(self):
        with patch('universal_led.wifi_switch_reservations._sync_directory',
                   side_effect=OSError('directory sync failed')):
            with self.assertRaises(OSError):
                self.reserve()
        self.assertFalse((self.directory / (TOKEN + '.json')).exists())

    def test_resolve_write_failure_preserves_pending(self):
        self.reserve()
        with patch('universal_led.wifi_switch_reservations.json.dump',
                   side_effect=OSError('interrupted replacement')):
            with self.assertRaises(OSError):
                resolve_switch(TOKEN, 'confirmed', directory=self.directory)
        self.assertEqual(json.loads((self.directory / (TOKEN + '.json')).read_text())['phase'],
                         'pending')
        self.assertFalse((self.directory / ('.' + TOKEN + '.tmp')).exists())

    def test_non_root_rejected(self):
        with patch('universal_led.wifi_switch_reservations.os.geteuid', return_value=1000):
            with self.assertRaises(PermissionError):
                self.reserve()


if __name__ == '__main__':
    unittest.main()
