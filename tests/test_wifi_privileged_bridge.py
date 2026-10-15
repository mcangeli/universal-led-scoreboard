"""Tests for privileged bridge fail-closed behavior; no real NetworkManager calls."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from universal_led.wifi_privileged_bridge import execute

UUID='11111111-1111-1111-1111-111111111111'

class BridgeTests(unittest.TestCase):
    def test_non_root_denied(self):
        with patch('universal_led.wifi_privileged_bridge.os.geteuid',return_value=1000):
            with self.assertRaises(PermissionError):
                execute({'action':'hotspot','enabled':True})

    def test_invalid_actions_denied(self):
        with patch('universal_led.wifi_privileged_bridge.os.geteuid',return_value=0):
            with self.assertRaises(ValueError):
                execute({'action':'arbitrary','command':'id'})

    def test_connection_does_not_arm_if_previous_mismatch(self):
        commands=[]
        def fake_run(args,**kwargs):
            commands.append(args)
            return SimpleNamespace(returncode=0,stdout='Different Network\n')
        data={'action':'connect_saved','interface':'wlan0',
              'previous_connection':'Original','target_ssid':'Target','profile_uuid':UUID}
        with patch('universal_led.wifi_privileged_bridge.os.geteuid',return_value=0):
            with self.assertRaisesRegex(ValueError,'does not match'):
                execute(data,run=fake_run)
        self.assertEqual(len(commands),1)

    def test_new_network_password_not_in_command_arguments(self):
        commands=[]
        def fake_run(args,**kwargs):
            commands.append((args,kwargs))
            return SimpleNamespace(returncode=0,stdout='Original\n')
        data={'action':'connect_new','interface':'wlan0',
              'previous_connection':'Original','target_ssid':'Target',
              'password':'test-password-123'}
        with patch('universal_led.wifi_privileged_bridge.os.geteuid',return_value=0), \
             patch('universal_led.wifi_recovery_scheduler.arm_recovery',return_value='a'*32):
            result=execute(data,run=fake_run)
        self.assertTrue(result['ok'])
        self.assertEqual(len(commands),2)
        self.assertNotIn('test-password-123',repr(commands[1][0]))
        self.assertEqual(commands[1][1]['input'],'test-password-123\n')

    def test_bad_password_rejected_before_nmcli(self):
        data={'action':'connect_new','interface':'wlan0',
              'previous_connection':'Original','target_ssid':'Target','password':'short'}
        with patch('universal_led.wifi_privileged_bridge.os.geteuid',return_value=0):
            with self.assertRaisesRegex(ValueError,'password'):
                execute(data)

if __name__=='__main__':
    unittest.main()
