import unittest
from types import SimpleNamespace
from unittest.mock import patch
from universal_led.wifi_privileged_bridge import execute
from universal_led.configurator import HTML

class HotspotPasswordTests(unittest.TestCase):
    def test_admin_page_has_password_confirmation(self):
        self.assertIn('id="hotspot-password"', HTML)
        self.assertIn('id="hotspot-confirm"', HTML)
        self.assertIn("action:'hotspot_password'", HTML)
    def test_rejects_weak_password(self):
        with patch('universal_led.wifi_privileged_bridge.os.geteuid', return_value=0):
            with self.assertRaisesRegex(ValueError,'8-63'):
                execute({'action':'hotspot_password','password':'short'})
    def test_password_not_in_argv_or_response(self):
        calls=[]
        def fake_run(args,**kwargs):
            calls.append((args,kwargs))
            return SimpleNamespace(returncode=0,stdout='ap\n')
        with patch('universal_led.wifi_privileged_bridge.os.geteuid', return_value=0):
            result=execute({'action':'hotspot_password','password':'ReadablePass24'},run=fake_run)
        self.assertTrue(result['ok'])
        self.assertNotIn('ReadablePass24',str(result))
        self.assertNotIn('ReadablePass24',str([args for args,_ in calls]))
        self.assertIn('ReadablePass24',calls[1][1]['input'])
    def test_missing_profile_fails_closed(self):
        def fake_run(args,**kwargs):
            return SimpleNamespace(returncode=10,stdout='')
        with patch('universal_led.wifi_privileged_bridge.os.geteuid', return_value=0):
            with self.assertRaisesRegex(ValueError,'missing'):
                execute({'action':'hotspot_password','password':'ReadablePass24'},run=fake_run)
if __name__=='__main__':
    unittest.main()
