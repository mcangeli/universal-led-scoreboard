"""Regression: scoreboard goal alerts survive delayed provider goal details."""
import unittest
from dataclasses import replace

from universal_led.scoring_alerts import ScoringAlerts
from universal_led.soccer import SoccerGoal, SoccerMatch
from universal_led.soccer_scoring_alerts import observe_soccer_match


def fixture(league, home=0, away=0, goals=(), status="live"):
    return SoccerMatch(match_id="fixture", league=league, home_id="HOME",
                       away_id="AWAY", home_score=home, away_score=away,
                       status=status, goals=tuple(goals))


class SoccerScoreFallbackTests(unittest.TestCase):
    def test_score_increase_announces_without_goal_event_and_no_late_duplicate(self):
        for league in ("MLS", "NWSL", "EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO"):
            with self.subTest(league=league):
                alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
                observe_soccer_match(alerts, fixture(league))
                observe_soccer_match(alerts, fixture(league, home=1))
                alert = alerts.next_alert(0)
                self.assertEqual((alert.league, alert.team_id, alert.kind),
                                 (league, "HOME", "GOAL"))
                observe_soccer_match(alerts, fixture(
                    league, home=1, goals=(SoccerGoal("late-goal", "HOME"),)))
                self.assertIsNone(alerts.next_alert(2))

    def test_first_snapshot_and_halftime_correction_do_not_announce(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        observe_soccer_match(alerts, fixture("MLS", home=2))
        observe_soccer_match(alerts, fixture("MLS", home=3, status="halftime"))
        observe_soccer_match(alerts, fixture("MLS", home=3))
        self.assertIsNone(alerts.next_alert(0))

    def test_authoritative_goal_keeps_provider_identity(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        observe_soccer_match(alerts, fixture("NWSL"))
        observe_soccer_match(alerts, fixture(
            "NWSL", away=1, goals=(SoccerGoal("official-1", "AWAY", scorer="Player"),)))
        self.assertEqual(alerts.next_alert(0).event_id, "official-1")

    def test_multiple_score_increase_creates_one_alert_per_goal(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        observe_soccer_match(alerts, fixture("MLS"))
        observe_soccer_match(alerts, fixture("MLS", home=2))
        self.assertNotEqual(alerts.next_alert(0).event_id, alerts.next_alert(2).event_id)
        self.assertIsNone(alerts.next_alert(4))


if __name__ == "__main__":
    unittest.main()
