"""Shared score-change observer regression tests."""
import unittest
from types import SimpleNamespace
from universal_led.score_change_observer import ScoreChangeObserver
from universal_led.scoring_alerts import ScoringAlerts


def game(status="live", away=0, home=0):
    return SimpleNamespace(game_id="game1", status=status, away="AWY", home="HOM",
                           away_score=away, home_score=home)


class ScoreChangeObserverTests(unittest.TestCase):
    def test_nhl_goal_detected_once(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        observer = ScoreChangeObserver(alerts, "nhl", "NHL", "GOAL")
        observer.observe((game(),))
        observer.observe((game(home=1),))
        self.assertEqual((alerts.next_alert(0).kind, alerts.next_alert(0).team_id),
                         ("GOAL", "HOM"))
        observer.observe((game(home=1),))
        self.assertIsNone(alerts.next_alert(2))

    def test_nfl_score_increase_and_correction(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=2)
        observer = ScoreChangeObserver(alerts, "nfl", "NFL")
        observer.observe((game(away=7),))
        observer.observe((game(away=10),))
        self.assertEqual(alerts.next_alert(0).team_id, "AWY")
        observer.observe((game(away=7),))
        self.assertIsNone(alerts.next_alert(2))

    def test_initial_and_final_snapshots_silent(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        observer = ScoreChangeObserver(alerts, "nhl", "NHL", "GOAL")
        observer.observe((game(home=2),))
        observer.observe((game(status="final", home=3),))
        self.assertIsNone(alerts.next_alert(0))

    def test_final_preserves_active_until_duration_completes(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=5)
        observer = ScoreChangeObserver(alerts, "nhl", "NHL", "GOAL")
        observer.observe((game(),))
        observer.observe((game(home=1),))
        self.assertIsNotNone(alerts.next_alert(0))
        observer.observe((game(status="final", home=1),))
        self.assertEqual(alerts.next_alert(1).kind, "GOAL")
        self.assertIsNone(alerts.next_alert(5))

    def test_postponement_cancels_pending(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=5)
        observer = ScoreChangeObserver(alerts, "nfl", "NFL")
        observer.observe((game(),))
        observer.observe((game(away=3),))
        observer.observe((game(status="postponed", away=3),))
        self.assertIsNone(alerts.next_alert(0))

    def test_favorites_scope_respected(self):
        alerts = ScoringAlerts(enabled=True, scope="favorites")
        observer = ScoreChangeObserver(alerts, "nhl", "NHL", "GOAL")
        observer.observe((game(),))
        observer.observe((game(home=1),), favorite_teams=("AWY",))
        self.assertIsNone(alerts.next_alert(0))


if __name__ == "__main__":
    unittest.main()
