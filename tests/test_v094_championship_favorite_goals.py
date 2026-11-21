"""Championship favorite-goal integration tests with realistic club identifiers."""
import unittest

from universal_led.scoring_alerts import ScoringAlerts, ScoreEvent
from universal_led.scoring_alert_eligibility import scoring_event_eligible


class ChampionshipFavoriteGoalTests(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "sports": {"english": {"enabled": True}},
            "english": {"mode": "favorite", "favorite_teams": ["espn:555"]},
        }
        self.alerts = ScoringAlerts(enabled=True, scope="favorites")
        self.alerts.set_eligibility(lambda e: scoring_event_eligible(e, self.settings))

    def goal(self, game, scorer, home="WRE", away="OTH", home_key="espn:555",
             away_key="espn:777", event_id="goal1"):
        return ScoreEvent("soccer", "CHAMPIONSHIP", game, event_id, scorer,
                          "GOAL", home_team=home, away_team=away,
                          home_club_key=home_key, away_club_key=away_key)

    def test_favorite_scores_with_provider_club_key(self):
        event = self.goal("1", "WRE")
        self.alerts.observe("soccer", "CHAMPIONSHIP", "1", ())
        self.assertEqual(self.alerts.observe("soccer", "CHAMPIONSHIP", "1", (event,)),
                         (event,))

    def test_opponent_scores_in_favorite_match(self):
        event = self.goal("2", "OTH")
        self.alerts.observe("soccer", "CHAMPIONSHIP", "2", ())
        self.assertEqual(self.alerts.observe("soccer", "CHAMPIONSHIP", "2", (event,)),
                         (event,))

    def test_unrelated_match_is_suppressed(self):
        event = self.goal("3", "OTH", home="AAA", away="OTH",
                          home_key="espn:111", away_key="espn:777")
        self.alerts.observe("soccer", "CHAMPIONSHIP", "3", ())
        self.assertEqual(self.alerts.observe("soccer", "CHAMPIONSHIP", "3", (event,)), ())
        self.assertIsNone(self.alerts.next_alert(0))

    def test_duplicate_goal_is_not_replayed(self):
        event = self.goal("4", "WRE")
        self.alerts.observe("soccer", "CHAMPIONSHIP", "4", ())
        self.assertEqual(len(self.alerts.observe("soccer", "CHAMPIONSHIP", "4", (event,))), 1)
        self.assertEqual(self.alerts.observe("soccer", "CHAMPIONSHIP", "4", (event,)), ())

    def test_alert_expires_and_returns_control_to_scheduler(self):
        event = self.goal("5", "OTH")
        self.alerts.observe("soccer", "CHAMPIONSHIP", "5", ())
        self.alerts.observe("soccer", "CHAMPIONSHIP", "5", (event,))
        self.assertEqual(self.alerts.next_alert(0), event)
        self.assertIsNone(self.alerts.next_alert(9))

    def test_favorite_abbreviation_remains_supported(self):
        self.settings["english"]["favorite_teams"] = ["WRE"]
        self.assertTrue(scoring_event_eligible(self.goal("6", "OTH"), self.settings))


if __name__ == "__main__":
    unittest.main()
