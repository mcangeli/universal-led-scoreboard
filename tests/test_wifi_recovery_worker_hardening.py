"""Stage 19 worker hardening tests: never execute real NetworkManager commands."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from universal_led.wifi_recovery import recover, secure_open_state

TOKEN='9'*32

class WorkerHardeningTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)
        self.path=self.directory/(TOKEN+'.json')
        self.path.write_text(json.dumps({
            'token':TOKEN,'interface':'wlan0',
            'previous_connection':'Original','delay':0}),encoding='utf-8')
        self.path.chmod(0o600)

    def test_worker_refuses_symlink(self):
        target=self.directory/'target'
        self.path.rename(target)
        self.path.symlink_to(target)
        runner=Mock()
        with self.assertRaises(OSError):
            recover(TOKEN,state_dir=self.directory,sleep=lambda _:None,run=runner)
        runner.assert_not_called()

    def test_worker_refuses_insecure_mode(self):
        self.path.chmod(0o644)
        runner=Mock()
        with self.assertRaises(PermissionError):
            recover(TOKEN,state_dir=self.directory,sleep=lambda _:None,run=runner)
        runner.assert_not_called()

    def test_worker_refuses_hardlinked_file(self):
        os.link(self.path,self.directory/'other')
        runner=Mock()
        with self.assertRaises(PermissionError):
            recover(TOKEN,state_dir=self.directory,sleep=lambda _:None,run=runner)
        runner.assert_not_called()

    def test_worker_refuses_replaced_state_after_wait(self):
        runner=Mock()
        def swap(_):
            self.path.unlink()
            self.path.write_text(json.dumps({
                'token':TOKEN,'interface':'wlan0',
                'previous_connection':'Different','delay':0}),encoding='utf-8')
            self.path.chmod(0o600)
        self.assertFalse(recover(TOKEN,state_dir=self.directory,
                                 sleep=swap,run=runner))
        runner.assert_not_called()

    def test_failed_rollback_cannot_be_retried(self):
        runner=Mock(return_value=SimpleNamespace(returncode=1))
        self.assertFalse(recover(TOKEN,state_dir=self.directory,
                                 sleep=lambda _:None,run=runner))
        self.assertFalse(recover(TOKEN,state_dir=self.directory,
                                 sleep=lambda _:None,run=runner))
        self.assertEqual(runner.call_count,1)

    def test_executing_state_cannot_be_cancelled_by_retry(self):
        state=json.loads(self.path.read_text())
        state['phase']='executing'
        self.path.write_text(json.dumps(state))
        self.path.chmod(0o600)
        runner=Mock()
        self.assertFalse(recover(TOKEN,state_dir=self.directory,
                                 sleep=lambda _:None,run=runner))
        runner.assert_not_called()

    def test_secure_opener_accepts_private_file(self):
        with secure_open_state(self.path) as handle:
            self.assertEqual(json.load(handle)['token'],TOKEN)

if __name__=='__main__':
    unittest.main()
