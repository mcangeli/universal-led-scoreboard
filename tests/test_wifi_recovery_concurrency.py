"""Cross-process cancellation and rollback tests using only fake runners."""
import json
import multiprocessing as mp
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from universal_led.wifi_recovery import recover
from universal_led.wifi_recovery_cancellation import cancel_recovery

TOKEN='d'*32

def worker(directory, entered, release, output):
    def fake_run(*args, **kwargs):
        entered.set()
        if not release.wait(5):
            output.put(('timeout',False))
            return SimpleNamespace(returncode=1)
        return SimpleNamespace(returncode=0)
    try:
        outcome=recover(TOKEN,state_dir=Path(directory),sleep=lambda _:None,run=fake_run)
        output.put(('recovered',outcome))
    except BaseException as exc:
        output.put(('error',type(exc).__name__))

class ConcurrentRecoveryTests(unittest.TestCase):
    def test_cancellation_during_rollback_is_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/(TOKEN+'.json')
            path.write_text(json.dumps({'token':TOKEN,'interface':'wlan0',
                'previous_connection':'Home','delay':0}))
            context=mp.get_context('spawn')
            entered=context.Event()
            release=context.Event()
            output=context.Queue()
            process=context.Process(target=worker,args=(directory,entered,release,output))
            process.start()
            try:
                self.assertTrue(entered.wait(5),'Worker did not reach fake runner')
                self.assertFalse(cancel_recovery(TOKEN,state_dir=Path(directory)))
                release.set()
                self.assertEqual(output.get(timeout=5),('recovered',True))
            finally:
                release.set()
                process.join(6)
                if process.is_alive():
                    process.terminate()
                    process.join(3)
            self.assertEqual(process.exitcode,0)
            self.assertFalse(path.exists())

    def test_cancellation_before_worker_starts(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/(TOKEN+'.json')
            path.write_text(json.dumps({'token':TOKEN,'interface':'wlan0',
                'previous_connection':'Home','delay':0}))
            self.assertTrue(cancel_recovery(TOKEN,state_dir=Path(directory)))
            calls=[]
            self.assertFalse(recover(TOKEN,state_dir=Path(directory),
                                     sleep=lambda _:None,
                                     run=lambda *a,**k:calls.append(a)))
            self.assertEqual(calls,[])

if __name__=='__main__':
    unittest.main()
