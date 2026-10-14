"""Cross-process tests for Wi-Fi rollback state locking.

Only temporary JSON files and injected command runners are used. No network
commands are executed and no privileged recovery service is started.
"""
import json
import multiprocessing
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from universal_led.wifi_recovery import recover
from universal_led.wifi_recovery_cancellation import cancel_recovery

TOKEN = 'd' * 32


def recovery_child(directory, started, proceed, outcome):
    def pause(_seconds):
        started.set()
        if not proceed.wait(5):
            raise TimeoutError('Parent did not release worker')
    def runner(*_args, **_kwargs):
        outcome.put('command')
        return SimpleNamespace(returncode=0)
    result = recover(TOKEN, state_dir=Path(directory), sleep=pause, run=runner)
    outcome.put(('recovered', result))


def executing_child(directory, executing, proceed, outcome):
    def runner(*_args, **_kwargs):
        executing.set()
        if not proceed.wait(5):
            raise TimeoutError('Parent did not release execution')
        return SimpleNamespace(returncode=0)
    result = recover(TOKEN, state_dir=Path(directory), sleep=lambda _: None, run=runner)
    outcome.put(('recovered', result))


def already_cancelled_child(directory, outcome):
    def forbidden_runner(*_args, **_kwargs):
        raise AssertionError('Cancelled recovery attempted network command')
    outcome.put(('recovered', recover(
        TOKEN, state_dir=Path(directory), sleep=lambda _: None,
        run=forbidden_runner)))


class CrossProcessRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.state = self.directory / (TOKEN + '.json')
        self.state.write_text(json.dumps({
            'token': TOKEN, 'interface': 'wlan0',
            'previous_connection': 'Home', 'delay': 0
        }), encoding='utf-8')
        self.ctx = multiprocessing.get_context('fork')

    def run_child(self, target, signal):
        proceed = self.ctx.Event()
        outcome = self.ctx.Queue()
        process = self.ctx.Process(target=target, args=(
            str(self.directory), signal, proceed, outcome))
        process.start()
        self.addCleanup(self.cleanup_child, process, proceed)
        self.assertTrue(signal.wait(5), 'Child did not reach synchronization point')
        return process, proceed, outcome

    @staticmethod
    def cleanup_child(process, proceed):
        proceed.set()
        process.join(5)
        if process.is_alive():
            process.terminate()
            process.join(5)

    def test_cancellation_wins_while_worker_is_waiting(self):
        waiting = self.ctx.Event()
        process, proceed, outcome = self.run_child(recovery_child, waiting)
        self.assertTrue(cancel_recovery(TOKEN, state_dir=self.directory))
        proceed.set()
        process.join(5)
        self.assertEqual(process.exitcode, 0)
        self.assertEqual(outcome.get(timeout=2), ('recovered', False))
        self.assertFalse(self.state.exists())

    def test_execution_wins_and_cancellation_fails_closed(self):
        executing = self.ctx.Event()
        process, proceed, outcome = self.run_child(executing_child, executing)
        self.assertFalse(cancel_recovery(TOKEN, state_dir=self.directory))
        proceed.set()
        process.join(5)
        self.assertEqual(process.exitcode, 0)
        self.assertEqual(outcome.get(timeout=2), ('recovered', True))
        self.assertFalse(self.state.exists())

    def test_cancelled_state_stays_cancelled_across_processes(self):
        self.assertTrue(cancel_recovery(TOKEN, state_dir=self.directory))
        outcome = self.ctx.Queue()
        process = self.ctx.Process(target=already_cancelled_child,
                                   args=(str(self.directory), outcome))
        process.start()
        self.addCleanup(self.cleanup_child, process, self.ctx.Event())
        process.join(5)
        self.assertEqual(process.exitcode, 0)
        self.assertEqual(outcome.get(timeout=2), ('recovered', False))


if __name__ == '__main__':
    unittest.main()
