import unittest
from unittest.mock import patch
from universal_led.wifi_diagnostics import _split_nmcli, wifi_status
from universal_led.configurator import HTML

class WifiStatusReuseTests(unittest.TestCase):
    def test_escaped_connection_name(self):
        self.assertEqual(_split_nmcli(r'wlan0:wifi:connected:Home\\:Guest'),
                         ['wlan0','wifi','connected','Home:Guest'])

    def test_connected_network_status(self):
        with patch('universal_led.wifi_diagnostics._nmcli',
                   side_effect=['enabled\n','wlan0:wifi:connected:Home\\:Guest\n']):
            status=wifi_status()
        self.assertTrue(status['connected'])
        self.assertEqual(status['devices'][0]['connection'],'Home:Guest')
        self.assertIsNone(status['hotspot_active'])

    def test_unavailable(self):
        with patch('universal_led.wifi_diagnostics._nmcli',return_value=None):
            self.assertFalse(wifi_status()['available'])

    def test_ui_keeps_hotspot_disabled(self):
        self.assertIn('Fallback hotspot: not configured yet',HTML)
        self.assertIn('Connected: ',HTML)

if __name__=='__main__':
    unittest.main()
