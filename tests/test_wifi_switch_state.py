import unittest

from universal_led.wifi_switch_state import WifiSwitch, SwitchRegistry, SwitchPhase

def make_switch(token='a' * 32, interface='wlan0', deadline=100):
    return WifiSwitch(interface, 'Home WiFi', 'Guest WiFi', token, deadline)


class WifiSwitchStateTests(unittest.TestCase):
    def test_pending_initially(self):
        self.assertEqual(make_switch().phase, SwitchPhase.PENDING)

    def test_confirm_before_deadline(self):
        self.assertEqual(make_switch().confirm(99).phase, SwitchPhase.CONFIRMED)

    def test_confirm_at_deadline_rejected(self):
        with self.assertRaises(ValueError):
            make_switch().confirm(100)

    def test_confirm_after_deadline_rejected(self):
        with self.assertRaises(ValueError):
            make_switch().confirm(101)

    def test_expiry_is_explicit(self):
        self.assertEqual(make_switch().expire(100).phase, SwitchPhase.EXPIRED)

    def test_not_expired_early(self):
        self.assertEqual(make_switch().expire(99).phase, SwitchPhase.PENDING)

    def test_expired_cannot_confirm(self):
        with self.assertRaises(ValueError):
            make_switch().expire(100).confirm(99)

    def test_pending_can_mark_rollback(self):
        self.assertEqual(make_switch().mark_rolled_back().phase, SwitchPhase.ROLLED_BACK)

    def test_expired_can_mark_rollback(self):
        self.assertEqual(make_switch().expire(100).mark_rolled_back().phase, SwitchPhase.ROLLED_BACK)

    def test_confirmed_cannot_rollback(self):
        with self.assertRaises(ValueError):
            make_switch().confirm(99).mark_rolled_back()

    def test_duplicate_interface_rejected(self):
        registry = SwitchRegistry().prepare(make_switch(), 1)
        with self.assertRaises(ValueError):
            registry.prepare(make_switch(token='b' * 32), 2)

    def test_expired_interface_still_blocked_until_resolved(self):
        registry = SwitchRegistry().prepare(make_switch(), 1)
        with self.assertRaises(ValueError):
            registry.prepare(make_switch(token='b' * 32), 101)

    def test_resolved_interface_can_be_reused(self):
        registry = SwitchRegistry().prepare(make_switch(), 1)
        registry = registry.update(make_switch().confirm(2))
        self.assertEqual(len(registry.prepare(make_switch(token='b' * 32), 3).switches), 2)

    def test_duplicate_token_rejected(self):
        registry = SwitchRegistry().prepare(make_switch(), 1)
        with self.assertRaises(ValueError):
            registry.prepare(make_switch(interface='wlan1'), 2)

    def test_distinct_interfaces_allowed(self):
        registry = SwitchRegistry().prepare(make_switch(), 1)
        self.assertEqual(len(registry.prepare(make_switch(token='b' * 32, interface='wlan1'), 2).switches), 2)

    def test_past_deadline_rejected(self):
        with self.assertRaises(ValueError):
            SwitchRegistry().prepare(make_switch(), 100)

    def test_unknown_update_rejected(self):
        with self.assertRaises(ValueError):
            SwitchRegistry().update(make_switch())

    def test_bad_token_rejected(self):
        with self.assertRaises(ValueError):
            make_switch(token='../bad')

    def test_bad_deadline_rejected(self):
        with self.assertRaises(ValueError):
            make_switch(deadline=float('inf'))


if __name__ == '__main__':
    unittest.main()
