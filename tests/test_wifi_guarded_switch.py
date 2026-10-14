import unittest
from unittest.mock import Mock

from universal_led.wifi_guarded_switch import (
    prepare_guarded_switch, require_recovery_before_switch)

TOKEN='a'*32

class GuardedSwitchTests(unittest.TestCase):
    def setUp(self):
        self.request={'ssid':'New Wi-Fi','security':'WPA2','password':'testpass123'}
        self.status={'available':True,'devices':[{
            'device':'wlan0','state':'connected','connection':'Old Wi-Fi'}]}

    def test_preparation_arms_before_authorizing(self):
        arm=Mock(return_value=TOKEN)
        check=Mock(return_value=True)
        tx=prepare_guarded_switch(self.request,self.status,arm=arm,is_armed=check)
        arm.assert_called_once_with('wlan0','Old Wi-Fi')
        check.assert_called_once_with(TOKEN)
        self.assertTrue(tx.may_change_network)
        self.assertEqual(tx.previous_connection,'Old Wi-Fi')
        self.assertNotIn('testpass123',repr(tx))

    def test_refuse_unarmed_recovery(self):
        with self.assertRaises(RuntimeError):
            prepare_guarded_switch(self.request,self.status,
                                   arm=lambda *_:TOKEN,is_armed=lambda _:False)

    def test_refuse_scheduler_failure(self):
        def fail(*_):
            raise RuntimeError('systemd-run failed')
        with self.assertRaises(RuntimeError):
            prepare_guarded_switch(self.request,self.status,arm=fail,
                                   is_armed=lambda _:True)

    def test_refuse_switch_if_recovery_disappears(self):
        tx=prepare_guarded_switch(self.request,self.status,
                                  arm=lambda *_:TOKEN,is_armed=lambda _:True)
        with self.assertRaises(RuntimeError):
            require_recovery_before_switch(tx,is_armed=lambda _:False)

    def test_unarmed_transaction_never_authorized(self):
        from universal_led.wifi_switch_transaction import SwitchTransaction
        tx=SwitchTransaction('Old Wi-Fi','wlan0','New Wi-Fi')
        with self.assertRaises(RuntimeError):
            require_recovery_before_switch(tx,is_armed=lambda _:True)

    def test_valid_armed_transaction(self):
        tx=prepare_guarded_switch(self.request,self.status,
                                  arm=lambda *_:TOKEN,is_armed=lambda _:True)
        self.assertTrue(require_recovery_before_switch(tx,is_armed=lambda _:True))

    def test_invalid_request_never_arms(self):
        arm=Mock()
        with self.assertRaises(ValueError):
            prepare_guarded_switch({'ssid':'','security':'WPA2','password':'12345678'},
                                   self.status,arm=arm,is_armed=lambda _:True)
        arm.assert_not_called()

if __name__=='__main__':
    unittest.main()
