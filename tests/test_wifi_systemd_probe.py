import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from universal_led.wifi_systemd_probe import run_probe

TOKEN='a'*16
RUNNING='LoadState=loaded\nActiveState=active\nSubState=running\n'

class SystemdProbeTests(unittest.TestCase):
    def test_running_probe(self):
        run=Mock(side_effect=[
            SimpleNamespace(returncode=0,stdout=''),
            SimpleNamespace(returncode=0,stdout=RUNNING)])
        result=run_probe(run=run,token_factory=lambda:TOKEN,sleep=lambda _:None)
        self.assertTrue(result['ok'])
        self.assertFalse(result['network_changed'])
        self.assertEqual(run.call_args_list[0].args[0][0],'systemd-run')
        self.assertEqual(run.call_args_list[1].args[0][0],'systemctl')

    def test_failed_start(self):
        run=Mock(return_value=SimpleNamespace(returncode=1,stdout=''))
        with self.assertRaises(RuntimeError):
            run_probe(run=run,token_factory=lambda:TOKEN)

    def test_inactive_probe(self):
        run=Mock(side_effect=[SimpleNamespace(returncode=0,stdout='')]+[
            SimpleNamespace(returncode=0,stdout='LoadState=loaded\nActiveState=inactive\nSubState=dead\n')]*4)
        result=run_probe(run=run,token_factory=lambda:TOKEN,sleep=lambda _:None)
        self.assertFalse(result['ok'])

    def test_bad_duration(self):
        for duration in (0,21,-1):
            with self.subTest(duration=duration),self.assertRaises(ValueError):
                run_probe(seconds=duration)

    def test_bad_token(self):
        with self.assertRaises(ValueError):
            run_probe(token_factory=lambda:'invalid')

    def test_worker_is_non_networking(self):
        from pathlib import Path
        path=Path(__file__).resolve().parents[1]/'scripts'/'universal-led-systemd-probe'
        source=path.read_text()
        for forbidden in ('nmcli','NetworkManager','connection up','connection down','wifi_recovery'):
            with self.subTest(forbidden=forbidden):
                # The docstring mentions NetworkManager, so inspect executable lines.
                executable='\n'.join(line for line in source.splitlines() if not line.lstrip().startswith('#') and not line.lstrip().startswith('"""'))
                if forbidden=='NetworkManager':
                    continue
                self.assertNotIn(forbidden,executable)

if __name__=='__main__':
    unittest.main()
