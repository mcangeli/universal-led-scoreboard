import unittest
from unittest.mock import patch
from types import SimpleNamespace
from universal_led.wifi_scan import parse_scan,scan_networks,parse_iw_scan,_merge_networks
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
        calls=[]
        def fake_run(args,**kwargs):
            calls.append(args)
            if args[-2:]==['device','status']:
                return SimpleNamespace(returncode=0,stdout='wlan0:wifi\\n')
            if args[:4]==['nmcli','device','wifi','rescan']:
                return SimpleNamespace(returncode=0,stdout='')
            return SimpleNamespace(returncode=0,stdout='Home:80:WPA2:*\\nGuest:60:WPA2:\\n')
        with patch('universal_led.wifi_scan.subprocess.run',side_effect=fake_run):
            result=scan_networks()
        self.assertTrue(result['available'])
        self.assertEqual(len(result['networks']),2)
        self.assertEqual(calls[1],['nmcli','device','wifi','rescan','ifname','wlan0'])
        self.assertEqual(calls[2][-3:],['list','ifname','wlan0'])
    def test_iw_scan_discovers_additional_networks(self):
        output='''BSS 00:11:22:33:44:55(on wlan0) -- associated
        freq: 2452
        signal: -47.00 dBm
        SSID: FBI_Surveillance_Van
        RSN:
BSS 00:11:22:33:44:66(on wlan0)
        freq: 5765
        signal: -60.00 dBm
        SSID: Angeli IoT_5G
        RSN:
BSS 00:11:22:33:44:77(on wlan0)
        freq: 2452
        signal: -48.00 dBm
        SSID: Angeli IoT
        RSN:
'''
        results=parse_iw_scan(output)
        self.assertEqual(len(results),3)
        merged=_merge_networks([{'ssid':'FBI_Surveillance_Van','signal':61,'security':'WPA2','connected':True}],results)
        self.assertEqual(len(merged),3)
        self.assertTrue(merged[0]['connected'])
    def test_hidden_ssid_ignored(self):
        self.assertEqual(parse_iw_scan('BSS aa(on wlan0)\\n  SSID: \\n'),[])
    def test_ui(self):
        self.assertIn('scanWifi()',HTML)
        self.assertIn('wifi-networks',HTML)
        self.assertIn('/api/wifi/scan',HTML)

if __name__=='__main__':
    unittest.main()
