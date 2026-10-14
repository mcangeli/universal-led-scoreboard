import unittest

from universal_led.wifi_switch_transaction import SwitchPhase, SwitchTransaction

TOKEN='a'*32

class WifiSwitchTransactionTests(unittest.TestCase):
    def setUp(self):
        self.tx=SwitchTransaction('Old Network','wlan0','New Network')

    def test_unarmed_cannot_switch(self):
        self.assertFalse(self.tx.may_change_network)
        with self.assertRaises(ValueError):
            self.tx.transition('switch')

    def test_valid_arming_then_switch(self):
        armed=self.tx.transition('arm',recovery_token=TOKEN)
        self.assertTrue(armed.may_change_network)
        switched=armed.transition('switch')
        self.assertEqual(switched.phase,SwitchPhase.SWITCH_REQUESTED)
        self.assertFalse(switched.may_cancel_recovery)

    def test_reject_invalid_token(self):
        for token in ('',None,'z'*32,'a'*31):
            with self.subTest(token=token),self.assertRaises(ValueError):
                self.tx.transition('arm',recovery_token=token)

    def test_association_not_confirmation(self):
        tx=self.tx.transition('arm',recovery_token=TOKEN).transition('switch').transition('associated')
        self.assertFalse(tx.may_cancel_recovery)
        self.assertTrue(tx.transition('confirm').may_cancel_recovery)

    def test_failure_requires_recovery(self):
        tx=self.tx.transition('arm',recovery_token=TOKEN).transition('switch').transition('fail')
        self.assertEqual(tx.phase,SwitchPhase.RECOVERY_REQUIRED)
        self.assertFalse(tx.may_cancel_recovery)

    def test_no_confirmation_before_association(self):
        tx=self.tx.transition('arm',recovery_token=TOKEN).transition('switch')
        with self.assertRaises(ValueError):
            tx.transition('confirm')

    def test_no_repeat_switch_or_confirmation(self):
        tx=self.tx.transition('arm',recovery_token=TOKEN).transition('switch').transition('associated').transition('confirm')
        with self.assertRaises(ValueError):
            tx.transition('switch')
        with self.assertRaises(ValueError):
            tx.transition('confirm')

if __name__=='__main__':
    unittest.main()
