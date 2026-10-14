import unittest
from unittest.mock import patch
from universal_led.wifi_reference import diagnose

class ReferenceWifiTests(unittest.TestCase):
    def test_same_commands_as_original_configurator(self):
        with patch('universal_led.wifi_reference.command',side_effect=[
            {'returncode':0,'stdout':'','stderr':''},
            {'returncode':0,'stdout':'Cafe:75:WPA2:*','stderr':''}
        ]) as run:
            result=diagnose('wlan0')
        self.assertEqual(run.call_args_list[0].args[0],
                         ['nmcli','device','wifi','rescan','ifname','wlan0'])
        self.assertEqual(run.call_args_list[1].args[0],
                         ['nmcli','-t','-f','SSID,SIGNAL,SECURITY,IN-USE','device','wifi','list','ifname','wlan0'])
        self.assertEqual(result['listing']['stdout'],'Cafe:75:WPA2:*')
