import unittest
from unittest.mock import Mock

from universal_led.wifi_verified_switch import (
    prepare_verified_switch, require_verified_switch)
from universal_led.wifi_switch_transaction import SwitchTransaction

TOKEN = 'a' * 32
REQUEST = {'ssid': 'New', 'security': 'WPA2', 'password': 'testpass123'}
STATUS = {'available': True, 'devices': [
    {'device': 'wlan0', 'state': 'connected', 'connection': 'Home'}]}

class VerifiedSwitchTests(unittest.TestCase):
    def test_prepares_only_after_verified_arming(self):
        arm = Mock(return_value=TOKEN)
        tx = prepare_verified_switch(REQUEST, STATUS, arm=arm)
        arm.assert_called_once_with('wlan0', 'Home')
        self.assertTrue(tx.may_change_network)
        self.assertEqual(tx.target_ssid, 'New')
        self.assertNotIn('testpass123', repr(tx))

    def test_invalid_request_never_arms(self):
        arm = Mock()
        with self.assertRaises(ValueError):
            prepare_verified_switch({'ssid': '', 'security': 'WPA2'}, STATUS, arm=arm)
        arm.assert_not_called()

    def test_failed_arming_denied(self):
        def fail(*_):
            raise RuntimeError('worker unavailable')
        with self.assertRaises(RuntimeError):
            prepare_verified_switch(REQUEST, STATUS, arm=fail)

    def test_rechecks_worker_and_state(self):
        tx = prepare_verified_switch(REQUEST, STATUS, arm=lambda *_: TOKEN)
        pending = Mock(return_value=True)
        inspect = Mock(return_value={'armed': True})
        self.assertTrue(require_verified_switch(tx, pending=pending, inspect=inspect))
        pending.assert_called_once_with(TOKEN)
        inspect.assert_called_once_with(TOKEN)

    def test_missing_state_fails_closed(self):
        tx = prepare_verified_switch(REQUEST, STATUS, arm=lambda *_: TOKEN)
        inspect = Mock()
        with self.assertRaises(RuntimeError):
            require_verified_switch(tx, pending=lambda _: False, inspect=inspect)
        inspect.assert_not_called()

    def test_stopped_worker_fails_closed(self):
        tx = prepare_verified_switch(REQUEST, STATUS, arm=lambda *_: TOKEN)
        with self.assertRaises(RuntimeError):
            require_verified_switch(tx, pending=lambda _: True,
                                    inspect=lambda _: {'armed': False})

    def test_unarmed_transaction_denied(self):
        tx = SwitchTransaction('Home', 'wlan0', 'New')
        with self.assertRaises(RuntimeError):
            require_verified_switch(tx, pending=lambda _: True,
                                    inspect=lambda _: {'armed': True})

if __name__ == '__main__':
    unittest.main()
