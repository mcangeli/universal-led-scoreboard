"""Standings cache and background refresh regression tests."""
import unittest

from universal_led.football_standings_runtime import FootballStandingsCache, BackgroundFootballStandings


class FootballStandingsRuntimeTests(unittest.TestCase):
    def test_initial_refresh_and_cached_reads_do_not_refetch(self):
        calls = []
        now = [0]
        def fetch(league):
            calls.append(league)
            return ["one"]
        cache = FootballStandingsCache("EPL", fetcher=fetch, clock=lambda: now[0])
        self.assertEqual(cache.rows(), ())
        self.assertEqual(cache.refresh(), ("one",))
        self.assertEqual(cache.rows(), ("one",))
        now[0] = 10
        self.assertEqual(cache.refresh(), ("one",))
        self.assertEqual(calls, ["EPL"])

    def test_refresh_after_interval(self):
        now = [0]
        calls = []
        def fetch(league):
            calls.append(league)
            return [len(calls)]
        cache = FootballStandingsCache("EPL", fetcher=fetch, refresh_seconds=60,
                                       clock=lambda: now[0])
        self.assertEqual(cache.refresh(), (1,))
        now[0] = 60
        self.assertEqual(cache.refresh(), (2,))

    def test_provider_error_retains_last_good_standings(self):
        now = [0]
        def fetch(league):
            if now[0] > 0:
                raise OSError("temporary outage")
            return ["cached"]
        cache = FootballStandingsCache("EPL", fetcher=fetch, refresh_seconds=60,
                                       clock=lambda: now[0])
        cache.refresh()
        now[0] = 60
        self.assertEqual(cache.refresh(), ("cached",))
        self.assertEqual(cache.rows(), ("cached",))
        self.assertEqual(cache.status()["state"], "error")
        self.assertIn("temporary outage", cache.status()["error"])

    def test_success_clears_previous_error(self):
        attempts = [0]
        def fetch(league):
            attempts[0] += 1
            if attempts[0] == 1:
                raise OSError("offline")
            return ["restored"]
        cache = FootballStandingsCache("EPL", fetcher=fetch)
        cache.refresh(force=True)
        self.assertEqual(cache.refresh(force=True), ("restored",))
        self.assertEqual(cache.status()["state"], "running")
        self.assertIsNone(cache.status()["error"])

    def test_invalid_refresh_interval(self):
        with self.assertRaises(ValueError):
            FootballStandingsCache("EPL", refresh_seconds=0)

    def test_background_worker_stops_cleanly(self):
        from threading import Event
        called = Event()
        def fetch(league):
            called.set()
            return []
        cache = FootballStandingsCache("EPL", fetcher=fetch)
        worker = BackgroundFootballStandings(cache)
        try:
            worker.start()
            self.assertTrue(called.wait(2))
        finally:
            worker.stop()
        self.assertFalse(worker._thread is not None)


if __name__ == "__main__":
    unittest.main()
