"""Soccer-to-shared-alert adapter regression tests."""
import unittest
from universal_led.soccer import SoccerMatch, SoccerGoal
from universal_led.scoring_alerts import ScoringAlerts
from universal_led.soccer_scoring_alerts import observe_soccer_match, soccer_score_events


def match(league="EPL", status="live", goals=()):
    return SoccerMatch(match_id="match-1", league=league, home_id="ARS",
                       away_id="MUN", home_score=len(goals), away_score=0,
                       status=status, goals=tuple(goals))


class SoccerScoringAlertTests(unittest.TestCase):
    def test_initial_snapshot_never_replays_historical_goals(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        goal = SoccerGoal("g1", "ARS", scorer="Player One")
        observe_soccer_match(alerts, match(goals=(goal,)))
        self.assertIsNone(alerts.next_alert(0))

    def test_live_confirmed_goal_is_announced_once(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        observe_soccer_match(alerts, match())
        goal = SoccerGoal("g1", "ARS", scorer="Player One")
        observe_soccer_match(alerts, match(goals=(goal,)))
        alert = alerts.next_alert(0)
        self.assertEqual((alert.league, alert.kind, alert.event_id), ("EPL", "GOAL", "g1"))
        observe_soccer_match(alerts, match(goals=(goal,)))
        self.assertIsNone(alerts.next_alert(2))

    def test_halftime_correction_is_not_announced_after_resume(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        observe_soccer_match(alerts, match())
        goal = SoccerGoal("g1", "ARS")
        observe_soccer_match(alerts, match(status="halftime", goals=(goal,)))
        observe_soccer_match(alerts, match(status="live", goals=(goal,)))
        self.assertIsNone(alerts.next_alert(0))

    def test_final_score_correction_does_not_alert(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        observe_soccer_match(alerts, match())
        observe_soccer_match(alerts, match(status="final", goals=(SoccerGoal("g1", "ARS"),)))
        self.assertIsNone(alerts.next_alert(0))

    def test_favorite_scope_uses_scoring_team(self):
        alerts = ScoringAlerts(enabled=True, scope="favorites")
        observe_soccer_match(alerts, match())
        observe_soccer_match(alerts, match(goals=(SoccerGoal("g1", "ARS"),)),
                             favorite_teams=("MUN",))
        self.assertIsNone(alerts.next_alert(0))

    def test_own_goal_is_labeled(self):
        alert = soccer_score_events(match(goals=(SoccerGoal("g1", "MUN", own_goal=True),)))[0]
        self.assertEqual(alert.kind, "OWN GOAL")

    def test_league_identity_is_preserved(self):
        for league in ("MLS", "NWSL", "EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO"):
            with self.subTest(league=league):
                alert = soccer_score_events(match(league=league, goals=(SoccerGoal("g1", "ARS"),)))[0]
                self.assertEqual(alert.league, league)


if __name__ == "__main__":
    unittest.main()
