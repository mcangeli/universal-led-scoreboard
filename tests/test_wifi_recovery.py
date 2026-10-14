import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from types import SimpleNamespace
from universal_led.wifi_recovery import recover, valid_token

TOKEN='a'*32

class WifiRecoveryTests(unittest.TestCase):
    def test_token_validation(self):
        self.assertTrue(valid_token(TOKEN))
        self.assertFalse(valid_token('../etc/passwd'))
        self.assertFalse(valid_token('A'*32))

    def test_expired_unconfirmed_switch_restores_previous_connection(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/(TOKEN+'.json')
            path.write_text(json.dumps({'token':TOKEN,'previous_connection':'Original Wi-Fi',
                                        'interface':'wlan0','delay':0}))
            path.chmod(0o600)
            runner=Mock(return_value=SimpleNamespace(returncode=0))
            self.assertTrue(recover(TOKEN,state_dir=Path(temp),sleep=lambda _:None,run=runner))
            self.assertEqual(runner.call_args.args[0],
                             ['nmcli','connection','up','id','Original Wi-Fi','ifname','wlan0'])
            self.assertFalse(path.exists())

    def test_failed_rollback_retains_state(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/(TOKEN+'.json')
            path.write_text(json.dumps({'token':TOKEN,'previous_connection':'Original',
                                        'interface':'wlan0','delay':0}))
            path.chmod(0o600)
            runner=Mock(return_value=SimpleNamespace(returncode=1))
            self.assertFalse(recover(TOKEN,state_dir=Path(temp),sleep=lambda _:None,run=runner))
            self.assertTrue(path.exists())

    def test_confirmed_switch_does_not_rollback(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/(TOKEN+'.json')
            path.write_text(json.dumps({'token':TOKEN,'previous_connection':'Original',
                                        'interface':'wlan0','delay':0}))
            path.chmod(0o600)
            runner=Mock()
            def confirm(_): path.unlink()
            self.assertFalse(recover(TOKEN,state_dir=Path(temp),sleep=confirm,run=runner))
            runner.assert_not_called()

    def test_missing_state_before_start_is_cancelled(self):
        with tempfile.TemporaryDirectory() as temp:
            runner=Mock()
            self.assertFalse(recover(TOKEN,state_dir=Path(temp),
                                     sleep=lambda _:None,run=runner))
            runner.assert_not_called()

    def test_invalid_recovery_state_does_not_execute(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/(TOKEN+'.json')
            path.write_text(json.dumps({'token':TOKEN,'previous_connection':'Original',
                                        'interface':'eth0','delay':0}))
            path.chmod(0o600)
            runner=Mock()
            with self.assertRaises(ValueError):
                recover(TOKEN,state_dir=Path(temp),sleep=lambda _:None,run=runner)
            runner.assert_not_called()

if __name__=='__main__':
    unittest.main()
