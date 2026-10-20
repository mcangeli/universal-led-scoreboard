"""Regression: a final feed update must not erase an unseen scoring alert."""
import unittest
from types import SimpleNamespace
from universal_led.scoring_alerts import ScoringAlerts
from universal_led.score_change_observer import NHLGoalObserver


def game(score, status="live"):
    return SimpleNamespace(game_id="final-1", away="BOS", home="NYR",
                           away_score=score, home_score=0, status=status)


class FinalScoreAlertDeliveryTests(unittest.TestCase):
    def test_pending_goal_survives_final_transition(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=5)
        observer = NHLGoalObserver(alerts)
        observer.observe([game(0)])
        observer.observe([game(1)])
        observer.observe([game(1, "final")])
        self.assertEqual(alerts.next_alert(100).kind, "GOAL")
        self.assertIsNone(alerts.next_alert(105))

    def test_active_goal_survives_final_transition(self):
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=5)
        observer = NHLGoalObserver(alerts)
        observer.observe([game(0)])
        observer.observe([game(1)])
        self.assertEqual(alerts.next_alert(100).kind, "GOAL")
        observer.observe([game(1, "final")])
        self.assertEqual(alerts.next_alert(104).kind, "GOAL")
        self.assertIsNone(alerts.next_alert(105))

    def test_canceled_game_still_drops_pending_goal(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        observer = NHLGoalObserver(alerts)
        observer.observe([game(0)])
        observer.observe([game(1)])
        observer.observe([game(1, "canceled")])
        self.assertIsNone(alerts.next_alert(100))


if __name__ == "__main__":
    unittest.main()
