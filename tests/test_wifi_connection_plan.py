import unittest
from universal_led.wifi_connection_plan import (
    ConnectionPlan, plan_connection, rollback_commands, verify_connection)

class WifiConnectionPlanTests(unittest.TestCase):
    def setUp(self):
        self.status={'available':True,'devices':[{
            'device':'wlan0','state':'connected','connection':'Old Network'}]}
        self.request={'ssid':'New Network','security':'WPA2','password':'password123'}

    def test_plan_preserves_old_connection(self):
        plan=plan_connection(self.request,self.status)
        self.assertEqual(plan.previous_connection,'Old Network')
        self.assertEqual(plan.interface,'wlan0')
        self.assertNotIn('password123',repr(plan))

    def test_rollback_restores_previous_profile(self):
        plan=plan_connection(self.request,self.status)
        self.assertEqual(rollback_commands(plan),
            [['nmcli','connection','up','id','Old Network','ifname','wlan0']])

    def test_refuse_when_offline(self):
        with self.assertRaises(ValueError):
            plan_connection(self.request,{'available':True,'devices':[]})

    def test_refuse_ambiguous_connections(self):
        with self.assertRaises(ValueError):
            plan_connection(self.request,{'available':True,'devices':
                self.status['devices']*2})

    def test_refuse_same_connection(self):
        request={**self.request,'ssid':'Old Network'}
        with self.assertRaises(ValueError):
            plan_connection(request,self.status)

    def test_verify(self):
        plan=plan_connection(self.request,self.status)
        self.assertFalse(verify_connection(plan,self.status))
        updated={'available':True,'devices':[{
            'device':'wlan0','state':'connected','connection':'New Network'}]}
        self.assertTrue(verify_connection(plan,updated))

    def test_rollback_is_mandatory(self):
        with self.assertRaises(ValueError):
            rollback_commands(ConnectionPlan('new','WPA2','wlan0','old',False))

if __name__=='__main__':
    unittest.main()
