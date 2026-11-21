"""Regression coverage for worker survival and restart after unexpected errors."""
import unittest
from datetime import date
from unittest.mock import Mock

from universal_led.nba_runtime import BackgroundNBAFeed
from universal_led.nhl_runtime import BackgroundNHLFeed


class FakeFeed:
    refresh_seconds = 5

    def __init__(self):
        self.calls = 0

    def refresh(self, day):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("simulated callback or date-provider failure")
        return ["recovered"]

    def status(self):
        return {"state": "running"}

    def games(self):
        return []


class WorkerRecoveryTests(unittest.TestCase):
    def test_nba_worker_continues_after_unexpected_error(self):
        self.check_worker(BackgroundNBAFeed)

    def test_nhl_worker_continues_after_unexpected_error(self):
        self.check_worker(BackgroundNHLFeed)

    def check_worker(self, worker_class):
        feed = FakeFeed()
        worker = worker_class(feed, day_provider=lambda: date(2026, 11, 21))
        observed = []
        def wait(_seconds):
            observed.append(feed.calls)
            if feed.calls >= 2:
                worker._stop.set()
        worker._stop.wait = wait
        worker._run()
        self.assertEqual(observed, [1, 2])
        self.assertEqual(feed.calls, 2)

    def test_nba_restarts_dead_thread(self):
        self.check_dead_thread_restart(BackgroundNBAFeed)

    def test_nhl_restarts_dead_thread(self):
        self.check_dead_thread_restart(BackgroundNHLFeed)

    def check_dead_thread_restart(self, worker_class):
        worker = worker_class(FakeFeed())
        dead = Mock()
        dead.is_alive.return_value = False
        worker._thread = dead
        worker._run = Mock()
        worker.start()
        try:
            self.assertIsNot(worker._thread, dead)
            worker._thread.join(timeout=2)
            worker._run.assert_called_once_with()
        finally:
            worker.stop()


if __name__ == "__main__":
    unittest.main()
