import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from universal_led.wifi_recovery_confirmation import confirm_recovery

TOKEN = 'd' * 32


class ConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state_dir = Path(self.tmp.name)

    def test_confirm_cancels_before_stopping_service(self):
        events = []
        def cancel(token, *, state_dir):
            events.append('cancel')
            self.assertEqual(token, TOKEN)
            self.assertEqual(state_dir, self.state_dir)
            return True
        def run(args, **kwargs):
            events.append('stop')
            self.assertEqual(args, ['systemctl', 'stop',
                                   'universal-led-wifi-recovery-' + TOKEN + '.service'])
            return SimpleNamespace(returncode=0)
        with patch('os.geteuid', return_value=0):
            result = confirm_recovery(TOKEN, state_dir=self.state_dir,
                                      cancel=cancel, run=run)
        self.assertEqual(events, ['cancel', 'stop'])
        self.assertEqual(result, {'confirmed': True, 'reason': 'confirmed',
                                  'unit_stopped': True})

    def test_rejected_cancellation_never_stops_worker(self):
        with patch('os.geteuid', return_value=0):
            result = confirm_recovery(TOKEN, state_dir=self.state_dir,
                                      cancel=lambda *a, **k: False,
                                      run=lambda *a, **k: self.fail('worker stopped'))
        self.assertFalse(result['confirmed'])
        self.assertFalse(result['unit_stopped'])

    def test_systemctl_failure_preserves_confirmed_result(self):
        with patch('os.geteuid', return_value=0):
            result = confirm_recovery(TOKEN, state_dir=self.state_dir,
                                      cancel=lambda *a, **k: True,
                                      run=lambda *a, **k: SimpleNamespace(returncode=1))
        self.assertTrue(result['confirmed'])
        self.assertEqual(result['reason'], 'stop_failed')

    def test_systemctl_timeout_preserves_confirmed_result(self):
        import subprocess
        def timeout(*args, **kwargs):
            raise subprocess.TimeoutExpired('systemctl', 12)
        with patch('os.geteuid', return_value=0):
            result = confirm_recovery(TOKEN, state_dir=self.state_dir,
                                      cancel=lambda *a, **k: True, run=timeout)
        self.assertTrue(result['confirmed'])
        self.assertEqual(result['reason'], 'stop_unverified')

    def test_root_required(self):
        with patch('os.geteuid', return_value=1000):
            with self.assertRaises(PermissionError):
                confirm_recovery(TOKEN, state_dir=self.state_dir)

    def test_invalid_token_rejected_without_side_effects(self):
        with patch('os.geteuid', return_value=0):
            with self.assertRaises(ValueError):
                confirm_recovery('../bad', state_dir=self.state_dir,
                                 cancel=lambda *a, **k: self.fail('cancel called'))

if __name__ == '__main__':
    unittest.main()
