import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from universal_led.wifi_probe_lifecycle import observe_probe_lifecycle

TOKEN='a'*16
RUNNING='LoadState=loaded\nActiveState=active\nSubState=running\n'
FINISHED='LoadState=loaded\nActiveState=active\nSubState=exited\nResult=success\n'
FAILED='LoadState=loaded\nActiveState=failed\nSubState=failed\nResult=exit-code\n'

def response(stdout='',returncode=0):
    return SimpleNamespace(stdout=stdout,returncode=returncode)

class ProbeLifecycleTests(unittest.TestCase):
    def test_start_completion_and_cleanup(self):
        run=Mock(side_effect=[response(),response(RUNNING),response(FINISHED),response()])
        result=observe_probe_lifecycle(run=run,sleep=lambda _:None,
                                       token_factory=lambda:TOKEN)
        self.assertTrue(result['ok'])
        self.assertTrue(result['completed'])
        self.assertFalse(result['network_changed'])
        self.assertEqual(run.call_args_list[-1].args[0][:3],
                         ['systemctl','--system','stop'])

    def test_failed_worker_is_not_success(self):
        run=Mock(side_effect=[response(),response(RUNNING),response(FAILED)])
        result=observe_probe_lifecycle(run=run,sleep=lambda _:None,
                                       token_factory=lambda:TOKEN)
        self.assertFalse(result['ok'])
        self.assertFalse(result['completed'])

    def test_failed_cleanup_is_not_success(self):
        run=Mock(side_effect=[response(),response(RUNNING),
                              response(FINISHED),response(returncode=1)])
        result=observe_probe_lifecycle(run=run,sleep=lambda _:None,
                                       token_factory=lambda:TOKEN)
        self.assertFalse(result['ok'])

    def test_timeout_does_not_claim_completion(self):
        run=Mock(side_effect=[response(),response(RUNNING),response(RUNNING)])
        result=observe_probe_lifecycle(run=run,sleep=lambda _:None,
                                       token_factory=lambda:TOKEN,polls=1)
        self.assertFalse(result['completed'])

    def test_invalid_poll_configuration(self):
        for polls in (0,61):
            with self.subTest(polls=polls),self.assertRaises(ValueError):
                observe_probe_lifecycle(polls=polls)
        with self.assertRaises(ValueError):
            observe_probe_lifecycle(interval=-1)

if __name__=='__main__':
    unittest.main()
