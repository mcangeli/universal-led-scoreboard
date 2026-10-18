"""v0.7 scoring alert foundation: independent, opt-in, event-ID-based queue."""
import unittest

from universal_led.scoring_alerts import ScoreEvent, ScoringAlerts
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.scoring_alert_screen import render_scoring_alert


def event(sport="soccer", league="EPL", game="42", eid="g1", team="ARS"):
    return ScoreEvent(sport, league, game, eid, team, "goal")


class ScoringAlertTests(unittest.TestCase):
    def test_disabled_by_default_and_no_historical_replay(self):
        alerts = ScoringAlerts()
        self.assertEqual(alerts.observe("soccer", "EPL", "42", [event()]), ())
        alerts.configure(enabled=True, scope="all")
        self.assertEqual(alerts.observe("soccer", "EPL", "42", [event()]), ())
        self.assertIsNone(alerts.next_alert(0))

    def test_new_event_interrupts_once_then_returns_to_rotation(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=5)
        alerts.observe("soccer", "EPL", "42", [])
        self.assertEqual(alerts.observe("soccer", "EPL", "42", [event()]), (event(),))
        self.assertEqual(alerts.next_alert(10), event())
        alerts.observe("soccer", "EPL", "42", [event()])
        self.assertEqual(alerts.next_alert(14), event())
        self.assertIsNone(alerts.next_alert(15))

    def test_favorites_only_does_not_alert_nonfavorites(self):
        alerts = ScoringAlerts(enabled=True, scope="favorites")
        alerts.observe("soccer", "EPL", "42", [])
        alerts.observe("soccer", "EPL", "42", [event()], favorite_teams=["MUN"])
        self.assertIsNone(alerts.next_alert(0))

    def test_favorites_first_without_discarding_other_games(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        for game in ("1", "2", "3"):
            alerts.observe("soccer", "EPL", game, [])
        first = event(game="1", eid="a", team="MUN")
        second = event(game="2", eid="b", team="CHE")
        favorite = event(game="3", eid="c", team="ARS")
        alerts.observe("soccer", "EPL", "1", [first], favorite_teams=["ARS"])
        alerts.observe("soccer", "EPL", "2", [second], favorite_teams=["ARS"])
        alerts.observe("soccer", "EPL", "3", [favorite], favorite_teams=["ARS"])
        self.assertEqual([alerts.next_alert(t).event_id for t in (0, 2, 4)], ["c", "a", "b"])
        self.assertIsNone(alerts.next_alert(6))

    def test_transient_missing_event_does_not_replay(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=1)
        alerts.observe("soccer", "EPL", "42", [])
        alerts.observe("soccer", "EPL", "42", [event()])
        self.assertEqual(alerts.next_alert(0), event())
        alerts.observe("soccer", "EPL", "42", [])
        alerts.observe("soccer", "EPL", "42", [event()])
        self.assertIsNone(alerts.next_alert(2))

    def test_disable_clears_pending_and_active(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        alerts.observe("soccer", "EPL", "42", [])
        alerts.observe("soccer", "EPL", "42", [event()])
        alerts.configure(enabled=False)
        self.assertIsNone(alerts.next_alert(0))

    def test_scheduler_interrupts_and_resumes_original_frame(self):
        class Renderer:
            def frame(self):
                return "normal-frame"
        clock = [0]
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=3)
        alerts.observe("soccer", "EPL", "42", [])
        alerts.observe("soccer", "EPL", "42", [event()])
        board = MultiSportRenderer(Renderer(), Renderer(), clock=lambda: clock[0],
                                   scoring_alerts=alerts,
                                   alert_renderer=lambda e: "ALERT:" + e.event_id)
        self.assertEqual(board.frame(), "ALERT:g1")
        clock[0] = 2
        self.assertEqual(board.frame(), "ALERT:g1")
        clock[0] = 3
        self.assertEqual(board.frame(), "normal-frame")

    def test_scheduler_uses_native_alert_renderer_and_resumes(self):
        class Renderer:
            def frame(self):
                return "normal-frame"
        clock = [0]
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=3)
        alerts.observe("soccer", "EPL", "42", [])
        alerts.observe("soccer", "EPL", "42", [event()])
        board = MultiSportRenderer(Renderer(), Renderer(), clock=lambda: clock[0],
                                   scoring_alerts=alerts)
        alert_frame = board.frame()
        self.assertEqual((alert_frame.width, alert_frame.height), (64, 32))
        self.assertTrue(any(pixel != (0, 0, 0)
                            for row in alert_frame.pixels for pixel in row))
        clock[0] = 3
        self.assertEqual(board.frame(), "normal-frame")

    def test_scheduler_without_alerts_is_unchanged(self):
        class Renderer:
            def frame(self):
                return "normal-frame"
        board = MultiSportRenderer(Renderer(), Renderer(), clock=lambda: 0)
        self.assertEqual(board.frame(), "normal-frame")

    def test_alert_screen_has_native_matrix_dimensions_and_visible_content(self):
        frame = render_scoring_alert(event())
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertTrue(any(pixel != (0, 0, 0)
                            for row in frame.pixels for pixel in row))

    def test_alert_screen_handles_untrusted_long_provider_description(self):
        scoring = ScoreEvent("soccer", "LEAGUE_ONE", "42", "goal", "ARS",
                             "goal", "A scorer scored! / 90+4")
        frame = render_scoring_alert(scoring)
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_invalid_event_identity_is_rejected(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        with self.assertRaises(ValueError):
            alerts.observe("soccer", "EPL", "99", [event()])
        with self.assertRaises(ValueError):
            event(eid="")

    def test_leagues_and_games_are_isolated(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=1)
        alerts.observe("soccer", "EPL", "42", [event()])
        other = event(league="MLS")
        alerts.observe("soccer", "MLS", "42", [other])
        self.assertIsNone(alerts.next_alert(0))
        newer = event(league="MLS", eid="g2")
        alerts.observe("soccer", "MLS", "42", [other, newer])
        self.assertEqual(alerts.next_alert(1), newer)


if __name__ == "__main__":
    unittest.main()
