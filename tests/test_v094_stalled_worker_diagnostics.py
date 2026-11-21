"""Stalled poller diagnostics never launch a second live worker."""
import unittest
from unittest.mock import Mock, patch

from universal_led.worker_watchdog import stalled_workers, restart_dead_workers


class StalledWorkerTests(unittest.TestCase):
    def worker(self, *, alive=True, started=100.0, interval=60):
        worker = Mock()
        worker._thread.is_alive.return_value = alive
        worker._poll_started = started
        worker.feed.refresh_seconds = interval
        return worker

    def test_active_poll_under_threshold_is_not_stalled(self):
        worker = self.worker()
        self.assertEqual(stalled_workers({"nba": worker}, now=280), ())

    def test_blocked_poll_is_reported(self):
        worker = self.worker()
        self.assertEqual(stalled_workers({"nba": worker}, now=281), ("nba",))
        self.assertEqual(restart_dead_workers({"nba": worker}), ())
        worker.start.assert_not_called()

    def test_completed_poll_is_not_stalled(self):
        worker = self.worker(started=None)
        self.assertEqual(stalled_workers({"nba": worker}, now=1000), ())

    def test_dead_worker_is_not_reported_as_blocked(self):
        worker = self.worker(alive=False)
        self.assertEqual(stalled_workers({"nba": worker}, now=1000), ())

    def test_one_probe_error_does_not_hide_other_stalls(self):
        broken = self.worker()
        broken._thread.is_alive.side_effect = RuntimeError("bad thread")
        stuck = self.worker()
        with patch("universal_led.worker_watchdog._LOG.exception"):
            self.assertEqual(stalled_workers({"nba": broken, "nhl": stuck}, now=281),
                             ("nhl",))


if __name__ == "__main__":
    unittest.main()
