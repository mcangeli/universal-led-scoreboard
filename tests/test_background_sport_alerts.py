"""Regression checks for MLB runs and NBA/WNBA lead changes."""
import unittest
from types import SimpleNamespace
from universal_led.mlb_score_alerts import MLBRunObserver
from universal_led.nba_engine import ConfiguredNBARenderer
from universal_led.scoring_alerts import ScoringAlerts


def baseball(away=0, home=0, status="live", pk=101):
    return SimpleNamespace(game_pk=pk, away="ATL", home="NYM",
                           away_runs=away, home_runs=home, status=status)


def basketball(away=0, home=0, status="live", gid="201"):
    return SimpleNamespace(game_id=gid, away="ATL", home="BOS",
                           away_score=away, home_score=home, status=status,
                           period=2, clock="5:00")


class BackgroundSportAlertsTests(unittest.TestCase):
    def test_mlb_baseline_repeat_and_run(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        observer = MLBRunObserver(alerts, lambda: ("ATL",))
        observer.observe((baseball(away=3),))
        self.assertIsNone(alerts.next_alert(0))
        observer.observe((baseball(away=3),))
        self.assertIsNone(alerts.next_alert(0))
        observer.observe((baseball(away=4),))
        event = alerts.next_alert(0)
        self.assertEqual((event.league, event.kind, event.team_id), ("MLB", "RUN", "ATL"))
        observer.observe((baseball(away=4),))
        self.assertIsNone(alerts.next_alert(2))

    def test_mlb_correction_and_final_silent(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        observer = MLBRunObserver(alerts)
        observer.observe((baseball(home=3),))
        observer.observe((baseball(home=2),))
        observer.observe((baseball(home=3, status="final"),))
        self.assertIsNone(alerts.next_alert(0))

    def test_mlb_favorite_scope(self):
        alerts = ScoringAlerts(enabled=True, scope="favorites")
        observer = MLBRunObserver(alerts, lambda: ("ATL",))
        observer.observe((baseball(),))
        observer.observe((baseball(home=1),))
        self.assertIsNone(alerts.next_alert(0))

    def test_basketball_background_lead_changes(self):
        for league in ("NBA", "WNBA"):
            with self.subTest(league=league):
                alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
                renderer = ConfiguredNBARenderer(
                    SimpleNamespace(games=lambda: []), scoring_alerts=alerts, league=league)
                renderer._observe_lead_changes((basketball(away=10, home=5),))
                self.assertIsNone(alerts.next_alert(0))
                renderer._observe_lead_changes((basketball(away=10, home=11),))
                event = alerts.next_alert(0)
                self.assertEqual((event.league, event.kind, event.team_id),
                                 (league, "LEAD", "BOS"))
                renderer._observe_lead_changes((basketball(away=10, home=11),))
                self.assertIsNone(alerts.next_alert(2))


if __name__ == "__main__":
    unittest.main()
