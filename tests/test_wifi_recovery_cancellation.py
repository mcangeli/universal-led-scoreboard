import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from universal_led.wifi_recovery import recover
from universal_led.wifi_recovery_cancellation import cancel_recovery

TOKEN='c'*32

class RecoveryCancellationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)
        self.path=self.directory/(TOKEN+'.json')
        self.path.write_text(json.dumps({
            'token':TOKEN,'interface':'wlan0',
            'previous_connection':'Home','delay':0}),encoding='utf-8')

    def test_cancel_before_worker_prevents_rollback(self):
        calls=[]
        self.assertTrue(cancel_recovery(TOKEN,state_dir=self.directory))
        self.assertFalse(recover(TOKEN,state_dir=self.directory,sleep=lambda _:None,
                                 run=lambda *a,**k:calls.append(a)))
        self.assertEqual(calls,[])

    def test_cancel_during_wait_prevents_rollback(self):
        calls=[]
        def cancel(_):
            self.assertTrue(cancel_recovery(TOKEN,state_dir=self.directory))
        self.assertFalse(recover(TOKEN,state_dir=self.directory,sleep=cancel,
                                 run=lambda *a,**k:calls.append(a)))
        self.assertEqual(calls,[])

    def test_cancellation_during_execution_is_too_late(self):
        results=[]
        def runner(*args,**kwargs):
            results.append(cancel_recovery(TOKEN,state_dir=self.directory))
            return SimpleNamespace(returncode=0)
        self.assertTrue(recover(TOKEN,state_dir=self.directory,sleep=lambda _:None,run=runner))
        self.assertEqual(results,[False])

    def test_failed_rollback_rejects_late_confirmation(self):
        def runner(*args,**kwargs):
            self.assertFalse(cancel_recovery(TOKEN,state_dir=self.directory))
            return SimpleNamespace(returncode=1)
        self.assertFalse(recover(TOKEN,state_dir=self.directory,sleep=lambda _:None,run=runner))
        self.assertTrue(self.path.exists())

    def test_invalid_token_rejected(self):
        with self.assertRaises(ValueError):
            cancel_recovery('../bad',state_dir=self.directory)

    def test_duplicate_cancellation_is_safe(self):
        self.assertTrue(cancel_recovery(TOKEN,state_dir=self.directory))
        self.assertFalse(cancel_recovery(TOKEN,state_dir=self.directory))

if __name__=='__main__':
    unittest.main()
