import unittest
from universal_led.wifi_provisioning import validate_connection_request,provisioning_readiness
from universal_led.configurator import HTML

class ProvisioningTests(unittest.TestCase):
    def test_secure_network(self):
        result=validate_connection_request({'ssid':'My Home','security':'WPA2','password':'examplepass'})
        self.assertEqual(result,{'ssid':'My Home','security':'WPA2','requires_password':True})
        self.assertNotIn('examplepass',str(result))
    def test_open_network(self):
        self.assertFalse(validate_connection_request({'ssid':'Guest','security':'Open'})['requires_password'])
    def test_bad_password_rejected(self):
        with self.assertRaises(ValueError):
            validate_connection_request({'ssid':'Home','security':'WPA2','password':'short'})
    def test_long_ssid_rejected(self):
        with self.assertRaises(ValueError):
            validate_connection_request({'ssid':'a'*33,'security':'Open'})
    def test_remote_changes_blocked(self):
        result=provisioning_readiness({'available':True,'devices':[{'state':'connected'}]})
        self.assertFalse(result['ready'])
    def test_ui_has_selection_but_no_active_connect(self):
        self.assertIn('selectWifiNetwork',HTML)
        self.assertIn('Connect (coming soon)',HTML)

if __name__=='__main__':
    unittest.main()
