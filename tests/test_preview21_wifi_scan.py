import unittest
from unittest.mock import patch
from types import SimpleNamespace
from universal_led.wifi_scan import parse_scan,scan_networks
from universal_led.configurator import HTML

class WifiScanTests(unittest.TestCase):
    def test_deduplicate_strongest(self):
        rows='Cafe:40:WPA2:\nCafe:80:WPA2:*\nGuest:55::\n'
        data=parse_scan(rows)
        self.assertEqual(len(data),2)
        self.assertEqual(data[0]['ssid'],'Cafe')
        self.assertTrue(data[0]['connected'])
        self.assertEqual(data[0]['signal'],80)
        self.assertEqual(data[1]['security'],'Open')
    def test_escaped_colon(self):
        self.assertEqual(parse_scan('Cafe\\:Guest:75:WPA2:\n')[0]['ssid'],'Cafe:Guest')
    def test_scan_unavailable(self):
        with patch('universal_led.wifi_scan.subprocess.run',side_effect=OSError()):
            self.assertFalse(scan_networks()['available'])
    def test_scan_requests_fresh_network_results(self):
        with patch('universal_led.wifi_scan.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='Home:80:WPA2:*\\nGuest:60:WPA2:\\n')) as runner:
            result=scan_networks()
        self.assertTrue(result['available'])
        self.assertEqual(len(result['networks']),2)
        command=runner.call_args.args[0]
        self.assertEqual(command[command.index('--rescan')+1],'yes')
    def test_ui(self):
        self.assertIn('scanWifi()',HTML)
        self.assertIn('wifi-networks',HTML)
        self.assertIn('/api/wifi/scan',HTML)

if __name__=='__main__':
    unittest.main()
