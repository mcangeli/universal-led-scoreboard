"""Dead-thread watchdog tests. Never restart a live or intentionally stopped worker."""
import unittest
from unittest.mock import Mock

from universal_led.worker_watchdog import restart_dead_workers


class WorkerWatchdogTests(unittest.TestCase):
    def test_dead_worker_is_restarted(self):
        worker = Mock()
        worker._thread.is_alive.return_value = False
        self.assertEqual(restart_dead_workers({"nba": worker}), ("nba",))
        worker.start.assert_called_once_with()

    def test_healthy_worker_is_not_restarted(self):
        worker = Mock()
        worker._thread.is_alive.return_value = True
        self.assertEqual(restart_dead_workers({"nhl": worker}), ())
        worker.start.assert_not_called()

    def test_unstarted_worker_is_not_started(self):
        worker = Mock()
        worker._thread = None
        self.assertEqual(restart_dead_workers({"mls": worker}), ())
        worker.start.assert_not_called()

    def test_failed_restart_does_not_block_another_dead_worker(self):
        failed = Mock()
        failed._thread.is_alive.return_value = False
        failed.start.side_effect = RuntimeError("restart failure")
        recovered = Mock()
        recovered._thread.is_alive.return_value = False
        with unittest.mock.patch("universal_led.worker_watchdog._LOG.exception"):
            result = restart_dead_workers({"nba": failed, "nhl": recovered})
        self.assertEqual(result, ("nhl",))
        failed.start.assert_called_once_with()
        recovered.start.assert_called_once_with()

    def test_thread_probe_failure_does_not_block_another_worker(self):
        failed = Mock()
        failed._thread.is_alive.side_effect = RuntimeError("thread probe failure")
        recovered = Mock()
        recovered._thread.is_alive.return_value = False
        with unittest.mock.patch("universal_led.worker_watchdog._LOG.exception"):
            result = restart_dead_workers({"nba": failed, "nhl": recovered})
        self.assertEqual(result, ("nhl",))
        recovered.start.assert_called_once_with()

    def test_one_failed_worker_does_not_restart_healthy_worker(self):
        dead = Mock()
        dead._thread.is_alive.return_value = False
        healthy = Mock()
        healthy._thread.is_alive.return_value = True
        self.assertEqual(restart_dead_workers({"nba": dead, "nhl": healthy}),
                         ("nba",))
        healthy.start.assert_not_called()


if __name__ == "__main__":
    unittest.main()
