import unittest
from unittest.mock import Mock

from universal_led.wifi_verified_recovery import arm_and_verify

TOKEN='a'*32

class VerifiedRecoveryTests(unittest.TestCase):
    def test_active_worker_accepted(self):
        arm=Mock(return_value=TOKEN)
        token=arm_and_verify('wlan0','Home',arm=arm,
            inspect=lambda _: {'armed':True},pending=lambda _:True)
        self.assertEqual(token,TOKEN)
        arm.assert_called_once_with('wlan0','Home')

    def test_pending_state_missing_denied(self):
        inspect=Mock(return_value={'armed':True})
        with self.assertRaises(RuntimeError):
            arm_and_verify('wlan0','Home',arm=lambda *_:TOKEN,
                inspect=inspect,pending=lambda _:False)
        inspect.assert_not_called()

    def test_worker_never_active_denied(self):
        inspect=Mock(return_value={'armed':False})
        with self.assertRaises(RuntimeError):
            arm_and_verify('wlan0','Home',arm=lambda *_:TOKEN,
                inspect=inspect,pending=lambda _:True,sleep=lambda _:None,attempts=3)
        self.assertEqual(inspect.call_count,3)

    def test_worker_eventually_active(self):
        inspect=Mock(side_effect=[{'armed':False},{'armed':True}])
        self.assertEqual(arm_and_verify('wlan0','Home',arm=lambda *_:TOKEN,
            inspect=inspect,pending=lambda _:True,sleep=lambda _:None),TOKEN)
        self.assertEqual(inspect.call_count,2)

    def test_state_disappears_after_worker_active(self):
        pending=Mock(side_effect=[True,False])
        with self.assertRaises(RuntimeError):
            arm_and_verify('wlan0','Home',arm=lambda *_:TOKEN,
                inspect=lambda _: {'armed':True},pending=pending)

    def test_scheduler_failure_propagates(self):
        def fail(*_): raise RuntimeError('systemd-run failed')
        with self.assertRaises(RuntimeError):
            arm_and_verify('wlan0','Home',arm=fail)

    def test_invalid_retry_limits(self):
        for attempts in (0,21,-1):
            with self.subTest(attempts=attempts),self.assertRaises(ValueError):
                arm_and_verify('wlan0','Home',attempts=attempts)

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            arm_and_verify('wlan0','Home',interval=-1)

if __name__=='__main__':
    unittest.main()
