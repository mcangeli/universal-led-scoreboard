"""Deterministic fault-injection coverage for multisport feed isolation.

These tests exercise cached feed adapters; they perform no network calls.
"""
import unittest

from universal_led.multisport_runtime import MultiSportRenderer


class FlakyAdapter:
    def __init__(self, name, *, live=False, games=True):
        self.name = name
        self.live = live
        self.games = games
        self.fail_live = False
        self.fail_games = False

    def has_live_games(self):
        if self.fail_live:
            raise TimeoutError("simulated feed timeout")
        return self.live

    def has_games(self):
        if self.fail_games:
            raise ConnectionError("simulated network loss")
        return self.games

    def frame(self):
        return self.name


class FeedFaultIsolationTests(unittest.TestCase):
    def setUp(self):
        self.now = [0.0]
        self.mlb = FlakyAdapter("MLB")
        self.nhl = FlakyAdapter("NHL")
        self.nba = FlakyAdapter("NBA")
        self.runtime = MultiSportRenderer(
            self.mlb, self.nhl, nba_renderer=self.nba,
            clock=lambda: self.now[0])
        self.runtime.configure_rotation(
            ("mlb", "nhl", "nba"), interval=10, preferred="mlb")

    def test_failed_live_probe_does_not_hide_other_live_sport(self):
        self.mlb.fail_live = True
        self.nhl.live = True
        self.nba.live = False
        for second in (0, 10, 20, 30):
            self.now[0] = second
            self.assertEqual(self.runtime.frame(), "NHL")

    def test_failed_availability_probe_does_not_remove_sport(self):
        self.mlb.fail_games = True
        self.nhl.games = False
        self.nba.games = False
        self.assertEqual(self.runtime.frame(), "MLB")

    def test_feed_recovers_without_recreating_renderer(self):
        self.mlb.fail_live = True
        self.nhl.live = True
        self.assertEqual(self.runtime.frame(), "NHL")
        self.mlb.fail_live = False
        self.mlb.live = True
        self.now[0] = 10
        self.assertEqual(self.runtime.frame(), "NHL")
        self.nhl.live = False
        self.now[0] = 20
        self.assertEqual(self.runtime.frame(), "MLB")

    def test_all_availability_probes_fail_without_crashing(self):
        for adapter in (self.mlb, self.nhl, self.nba):
            adapter.fail_games = True
            adapter.fail_live = True
        self.assertIn(self.runtime.frame(), ("MLB", "NHL", "NBA"))


if __name__ == "__main__":
    unittest.main()
