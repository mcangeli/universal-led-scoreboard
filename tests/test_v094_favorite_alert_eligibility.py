"""Regression tests: favorite-only game selection controls global scoring alerts."""
import unittest

from universal_led.scoring_alerts import ScoreEvent, ScoringAlerts
from universal_led.scoring_alert_eligibility import scoring_event_eligible


def event(sport, game, home, away, scorer):
    return ScoreEvent(sport, sport.upper(), game, "goal:1", scorer, "GOAL",
                      home_team=home, away_team=away)


class FavoriteAlertEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "sports": {sport: {"enabled": True} for sport in
                       ("mlb", "nhl", "nba", "wnba", "nfl", "mls", "nwsl", "english")},
            **{sport: {"mode": "favorite", "favorite_teams": ["ATL"]} for sport in
               ("mlb", "nhl", "nba", "wnba", "nfl", "mls", "nwsl", "english")},
        }
        self.alerts = ScoringAlerts(enabled=True, scope="all")
        self.alerts.set_eligibility(
            lambda item: scoring_event_eligible(item, self.settings))

    def test_nonfavorite_game_never_enters_queue(self):
        other = event("nhl", "1", "BOS", "NYR", "BOS")
        self.alerts.observe("nhl", "NHL", "1", ())
        self.assertEqual(self.alerts.observe("nhl", "NHL", "1", (other,)), ())
        self.assertIsNone(self.alerts.next_alert(0))

    def test_opponent_goal_in_favorite_matchup_is_eligible(self):
        opponent = event("nhl", "2", "ATL", "BOS", "BOS")
        self.alerts.observe("nhl", "NHL", "2", ())
        self.assertEqual(self.alerts.observe("nhl", "NHL", "2", (opponent,)),
                         (opponent,))

    def test_queued_event_is_removed_after_switch_to_favorites(self):
        self.settings["nhl"]["mode"] = "all"
        other = event("nhl", "3", "BOS", "NYR", "BOS")
        self.alerts.observe("nhl", "NHL", "3", ())
        self.alerts.observe("nhl", "NHL", "3", (other,))
        self.settings["nhl"]["mode"] = "favorite"
        self.assertIsNone(self.alerts.next_alert(0))

    def test_active_event_is_cancelled_after_team_change(self):
        favorite = event("nhl", "4", "ATL", "BOS", "ATL")
        self.alerts.observe("nhl", "NHL", "4", ())
        self.alerts.observe("nhl", "NHL", "4", (favorite,))
        self.assertEqual(self.alerts.next_alert(0), favorite)
        self.settings["nhl"]["favorite_teams"] = ["NYR"]
        self.assertIsNone(self.alerts.next_alert(1))

    def test_disabled_sport_has_no_alerts(self):
        self.settings["sports"]["nhl"]["enabled"] = False
        self.assertFalse(scoring_event_eligible(
            event("nhl", "5", "ATL", "BOS", "ATL"), self.settings))

    def test_all_leagues_enforce_favorite_only(self):
        for sport in ("mlb", "nhl", "nba", "wnba", "nfl", "mls", "nwsl", "english"):
            with self.subTest(sport=sport):
                self.assertFalse(scoring_event_eligible(
                    event(sport, "x", "BOS", "NYR", "BOS"), self.settings))
                self.assertTrue(scoring_event_eligible(
                    event(sport, "y", "ATL", "NYR", "NYR"), self.settings))


if __name__ == "__main__":
    unittest.main()
