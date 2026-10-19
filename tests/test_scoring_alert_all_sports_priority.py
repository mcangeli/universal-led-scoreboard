"""Shared scoring announcement priority across all supported sports."""
import unittest
from universal_led.scoring_alerts import ScoreEvent, ScoringAlerts
from universal_led.multisport_runtime import MultiSportRenderer


class Renderer:
    def frame(self):
        return "normal"


class AllSportScoringPriorityTests(unittest.TestCase):
    def test_each_league_preempts_normal_rotation_and_expires(self):
        for sport, league, kind in (
            ("baseball", "MLB", "RUN"),
            ("basketball", "NBA", "SCORE"),
            ("basketball", "WNBA", "SCORE"),
            ("football", "NFL", "TOUCHDOWN"),
            ("hockey", "NHL", "GOAL"),
            ("soccer", "MLS", "GOAL"),
            ("soccer", "NWSL", "GOAL"),
            ("soccer", "EPL", "GOAL"),
            ("soccer", "CHAMPIONSHIP", "GOAL"),
            ("soccer", "LEAGUE_ONE", "GOAL"),
            ("soccer", "LEAGUE_TWO", "GOAL"),
        ):
            with self.subTest(league=league):
                now = [0]
                queue = ScoringAlerts(enabled=True, scope="all", seconds=3)
                board = MultiSportRenderer(Renderer(), Renderer(), clock=lambda: now[0],
                    scoring_alerts=queue, alert_renderer=lambda e: e.league + ":" + e.event_id)
                event = ScoreEvent(sport, league, "match-1", "event-1", "HOME", kind)
                queue.observe(sport, league, "match-1", ())
                queue.observe(sport, league, "match-1", (event,))
                self.assertEqual(board.frame(), league + ":event-1")
                now[0] = 2
                self.assertEqual(board.frame(), league + ":event-1")
                now[0] = 3
                self.assertEqual(board.frame(), "normal")
                queue.observe(sport, league, "match-1", (event,))
                self.assertEqual(board.frame(), "normal")


if __name__ == "__main__":
    unittest.main()
