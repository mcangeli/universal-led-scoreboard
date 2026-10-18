"""Integration tests for soccer renderer updates feeding cross-sport alerts."""
import unittest
from universal_led.scoring_alerts import ScoringAlerts
from universal_led.soccer import SoccerMatch, SoccerGoal
from universal_led.soccer_engine import ConfiguredSoccerRenderer
from universal_led.english_rotation import EnglishFootballRenderer


class Feed:
    def games(self):
        return ()


def match(league, goals=(), status="live"):
    return SoccerMatch(match_id="fixture-1", league=league, home_id="ARS",
                       away_id="MUN", home_score=len(goals), away_score=0,
                       status=status, goals=tuple(goals))


class SoccerRendererAlertIntegrationTests(unittest.TestCase):
    def test_mls_and_nwsl_update_deliver_confirmed_goal(self):
        for league in ("MLS", "NWSL"):
            with self.subTest(league=league):
                alerts = ScoringAlerts(enabled=True, scope="all")
                renderer = ConfiguredSoccerRenderer(Feed(), league=league,
                                                     scoring_alerts=alerts)
                renderer.update(match(league))
                renderer.update(match(league, (SoccerGoal("goal-1", "ARS"),)))
                self.assertEqual(alerts.next_alert(0).league, league)

    def test_english_divisions_update_deliver_confirmed_goal(self):
        for league in ("EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO"):
            with self.subTest(league=league):
                alerts = ScoringAlerts(enabled=True, scope="all")
                renderer = EnglishFootballRenderer({league: Feed()},
                                                   scoring_alerts=alerts)
                renderer.update(match(league))
                renderer.update(match(league, (SoccerGoal("goal-1", "ARS"),)))
                self.assertEqual(alerts.next_alert(0).league, league)

    def test_disabled_alerts_do_not_interrupt_updates(self):
        alerts = ScoringAlerts()
        renderer = ConfiguredSoccerRenderer(Feed(), league="MLS",
                                             scoring_alerts=alerts)
        renderer.update(match("MLS"))
        renderer.update(match("MLS", (SoccerGoal("goal-1", "ARS"),)))
        self.assertIsNone(alerts.next_alert(0))

    def test_english_disabled_division_cannot_queue_alert(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        renderer = EnglishFootballRenderer({"EPL": Feed(), "CHAMPIONSHIP": Feed()},
                                           enabled=["EPL"], scoring_alerts=alerts)
        renderer.update(match("CHAMPIONSHIP"))
        renderer.update(match("CHAMPIONSHIP", (SoccerGoal("goal-1", "ARS"),)))
        self.assertIsNone(alerts.next_alert(0))


if __name__ == "__main__":
    unittest.main()
