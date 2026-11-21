"""Weather and news worker fault injection, without external requests."""
import threading
import unittest
from unittest.mock import Mock, patch

from universal_led.weather_worker import WeatherWorker
from universal_led.news_background import BackgroundNews


class SupplementalWorkerRecoveryTests(unittest.TestCase):
    def test_weather_refresh_exception_does_not_stop_worker(self):
        worker = WeatherWorker("/unused", wait_seconds=0.001)
        calls = []
        def refresh():
            calls.append(len(calls))
            if len(calls) == 1:
                raise RuntimeError("unexpected weather failure")
            worker._stop.set()
        worker.refresh = refresh
        with patch("universal_led.weather_worker._LOG.exception"):
            worker.start()
            worker._thread.join(timeout=2)
        self.assertEqual(len(calls), 2)
        worker.stop()

    def test_news_refresh_exception_preserves_worker(self):
        ticks = [0.0]
        news = BackgroundNews("/unused", automatic=Mock(), clock=lambda: ticks[0])
        news._next = -1
        calls = []
        def settings():
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("unexpected news failure")
            news._running = False
            return {}
        # The news loop's one-second sleep is patched so the test is fast.
        with patch("universal_led.news_background.load_news_settings",
                   return_value={"sources": []}), \
             patch("universal_led.news_background.time.sleep",
                   side_effect=lambda _: ticks.__setitem__(0, ticks[0] + 61)), \
             patch("universal_led.news_background._LOG.exception"):
            news.start(settings)
            news._thread.join(timeout=2)
        # A failed attempt is throttled for 60 seconds. The worker remains
        # alive until explicitly stopped; retry behavior is covered separately.
        self.assertEqual(len(calls), 2)
        news.stop()

    def test_news_start_replaces_dead_thread(self):
        news = BackgroundNews("/unused")
        news._running = True
        dead = Mock()
        dead.is_alive.return_value = False
        news._thread = dead
        with patch("universal_led.news_background.threading.Thread") as thread:
            thread.return_value.is_alive.return_value = True
            news.start(lambda: {})
        thread.assert_called_once()
        thread.return_value.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
