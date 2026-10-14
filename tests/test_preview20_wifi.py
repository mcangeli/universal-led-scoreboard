import unittest
from unittest.mock import patch
from universal_led.wifi_diagnostics import wifi_status
from universal_led.configurator import HTML

class Preview20WifiTests(unittest.TestCase):
    def test_nmcli_unavailable(self):
        with patch('universal_led.wifi_diagnostics._nmcli',return_value=None):
            self.assertFalse(wifi_status()['available'])
    def test_only_wifi_devices_and_no_password(self):
        with patch('universal_led.wifi_diagnostics._nmcli',
                   side_effect=['enabled\n','eth0:ethernet:connected:LAN\nwlan0:wifi:connected:Home\n']):
            result=wifi_status()
        self.assertEqual(result['devices'],[{'device':'wlan0','state':'connected','connection':'Home'}])
        self.assertNotIn('password',str(result).lower())
    def test_wifi_panel(self):
        self.assertIn('wifi-info',HTML)
        self.assertIn('/api/wifi',HTML)

if __name__=='__main__':
    unittest.main()
