"""End-to-end shared scoring queue and frame scheduler regression."""
import unittest
from types import SimpleNamespace
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.scoring_alerts import ScoringAlerts, ScoreEvent


class StubSport:
    def __init__(self, frame):
        self.value = frame
    def has_games(self):
        return True
    def has_live_games(self):
        return True
    def frame(self):
        return self.value


def event(sport, league, game, team, seq):
    return ScoreEvent(sport, league, game, str(seq), team, "SCORE")


class MultiSportAlertQueueTests(unittest.TestCase):
    def test_cross_sport_queue_and_return_to_live_rotation(self):
        now = [0.]
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        board = MultiSportRenderer(StubSport("MLB FRAME"), StubSport("NHL FRAME"),
                                  clock=lambda: now[0], scoring_alerts=alerts,
                                  alert_renderer=lambda e: e.league + ":" + e.event_id)
        board.configure_rotation(("mlb", "nhl"), interval=5)
        a = event("mlb", "MLB", "1", "ATL", 1)
        b = event("nhl", "NHL", "2", "BOS", 1)
        alerts.baseline("mlb", "MLB", "1", ())
        alerts.baseline("nhl", "NHL", "2", ())
        alerts.observe("mlb", "MLB", "1", (a,))
        self.assertEqual(board.frame(), "MLB:1")
        alerts.observe("nhl", "NHL", "2", (b,))
        self.assertEqual(board.frame(), "MLB:1")
        now[0] = 2
        self.assertEqual(board.frame(), "NHL:1")
        now[0] = 4
        self.assertEqual(board.frame(), "MLB FRAME")

    def test_favorites_queued_ahead_without_preempting_active(self):
        now = [0.]
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        board = MultiSportRenderer(StubSport("NORMAL"), StubSport("OTHER"),
                                  clock=lambda: now[0], scoring_alerts=alerts,
                                  alert_renderer=lambda e: e.event_id)
        for game in ("1", "2", "3"):
            alerts.baseline("mlb", "MLB", game, ())
        alerts.observe("mlb", "MLB", "1", (event("mlb", "MLB", "1", "NYM", "first"),))
        self.assertEqual(board.frame(), "first")
        alerts.observe("mlb", "MLB", "2", (event("mlb", "MLB", "2", "BOS", "second"),))
        alerts.observe("mlb", "MLB", "3", (event("mlb", "MLB", "3", "ATL", "favorite"),),
                       favorite_teams=("ATL",))
        self.assertEqual(board.frame(), "first")
        now[0] = 2
        self.assertEqual(board.frame(), "favorite")
        now[0] = 4
        self.assertEqual(board.frame(), "second")
        now[0] = 6
        self.assertEqual(board.frame(), "NORMAL")

    def test_alert_timer_begins_after_successful_render(self):
        now = [0.]
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=3)
        alerts.baseline("nhl", "NHL", "1", ())
        alerts.observe("nhl", "NHL", "1", (event("nhl", "NHL", "1", "BOS", "goal"),))
        def slow_draw(e):
            now[0] += 2
            return e.event_id
        board = MultiSportRenderer(StubSport("NORMAL"), StubSport("OTHER"),
                                  clock=lambda: now[0], scoring_alerts=alerts,
                                  alert_renderer=slow_draw)
        self.assertEqual(board.frame(), "goal")
        self.assertEqual(now[0], 2)
        # The three-second slot begins at successful render (t=2), not t=0.
        now[0] = 4
        self.assertEqual(board.frame(), "goal")
        now[0] = 5
        self.assertEqual(board.frame(), "NORMAL")

    def test_failed_alert_render_is_retried_for_full_duration(self):
        now = [0.]
        calls = [0]
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=3)
        alerts.baseline("nhl", "NHL", "1", ())
        goal = event("nhl", "NHL", "1", "BOS", "goal")
        alerts.observe("nhl", "NHL", "1", (goal,))

        def draw(e):
            calls[0] += 1
            if calls[0] == 1:
                raise RuntimeError("temporary renderer failure")
            return e.event_id

        board = MultiSportRenderer(StubSport("NORMAL"), StubSport("OTHER"),
                                  clock=lambda: now[0], scoring_alerts=alerts,
                                  alert_renderer=draw)
        with self.assertRaises(RuntimeError):
            board.frame()
        now[0] = 10
        self.assertEqual(board.frame(), "goal")
        now[0] = 12
        self.assertEqual(board.frame(), "goal")
        now[0] = 13
        self.assertEqual(board.frame(), "NORMAL")

    def test_disable_clears_pending_and_active(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        alerts.baseline("mlb", "MLB", "1", ())
        alerts.observe("mlb", "MLB", "1", (event("mlb", "MLB", "1", "ATL", 1),))
        self.assertIsNotNone(alerts.next_alert(0))
        alerts.configure(enabled=False)
        self.assertIsNone(alerts.next_alert(1))
        alerts.configure(enabled=True, scope="all", seconds=2)
        self.assertIsNone(alerts.next_alert(1))


if __name__ == "__main__":
    unittest.main()
