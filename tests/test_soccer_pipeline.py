"""End-to-end soccer polling to renderer goal-screen integration."""
import unittest
from datetime import date

from universal_led.soccer import SoccerGoal, SoccerMatch
from universal_led.soccer_engine import ConfiguredSoccerRenderer
from universal_led.soccer_runtime import BackgroundSoccerFeed


class StubFeed:
    refresh_seconds = 60

    def __init__(self, snapshots):
        self.snapshots = iter(snapshots)
        self.current = []

    def refresh(self, day):
        self.current = list(next(self.snapshots))
        return list(self.current)

    def games(self):
        return list(self.current)

    def status(self):
        return {"state": "running"}


class SoccerPipelineTests(unittest.TestCase):
    def test_poll_to_goal_to_match_screen(self):
        now = [100.0]
        baseline = SoccerMatch("fixture1", "MLS", "ATL", "MIA", 0, 0, "in")
        goal = SoccerGoal("goal1", "ATL", "Forward", "61'")
        scored = SoccerMatch("fixture1", "MLS", "ATL", "MIA", 1, 0, "in", (goal,))
        feed = StubFeed([[baseline], [scored], [scored]])
        renderer = ConfiguredSoccerRenderer(feed, league="MLS", clock=lambda: now[0])
        worker = BackgroundSoccerFeed(feed, day_provider=lambda: date(2026, 10, 17),
                                      on_match=renderer.update)
        worker.refresh_once()
        self.assertEqual(renderer.display.screen(baseline, now[0]).kind, "match")
        worker.refresh_once()
        self.assertEqual(renderer.display.screen(scored, now[0]).kind, "goal")
        self.assertEqual(renderer.display.screen(scored, now[0]).line1, "Forward")
        worker.refresh_once()
        now[0] += 8
        self.assertEqual(renderer.display.screen(scored, now[0]).kind, "match")

    def test_initial_snapshot_never_replays_historical_goal(self):
        now = [5.0]
        old_goal = SoccerGoal("past", "POR", "Past Scorer")
        initial = SoccerMatch("fixture2", "NWSL", "POR", "SEA", 1, 0, "in", (old_goal,))
        feed = StubFeed([[initial]])
        renderer = ConfiguredSoccerRenderer(feed, league="NWSL", clock=lambda: now[0])
        worker = BackgroundSoccerFeed(feed, day_provider=lambda: date(2026, 10, 17),
                                      on_match=renderer.update)
        worker.refresh_once()
        self.assertEqual(renderer.display.screen(initial, now[0]).kind, "match")


if __name__ == "__main__":
    unittest.main()
