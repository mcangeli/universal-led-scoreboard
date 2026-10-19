"""v0.7.0 shared goal alert presentation regression tests."""
import unittest
from universal_led.scoring_alerts import ScoreEvent, ScoringAlerts
from universal_led.scoring_alert_screen import render_scoring_alert
from universal_led.soccer import SoccerMatch, SoccerGoal
from universal_led.soccer_scoring_alerts import observe_soccer_match


def match(goals=(), score=0):
    return SoccerMatch(match_id="fixture", league="EPL", home_id="TOT",
                       away_id="COV", home_score=score, away_score=0,
                       status="live", goals=goals)


class ScoringAlertLayoutTests(unittest.TestCase):
    def test_goal_carries_score_and_player(self):
        queue = ScoringAlerts(enabled=True, scope="all")
        observe_soccer_match(queue, match())
        observe_soccer_match(queue, match((SoccerGoal("goal-1", "TOT", scorer="A Player"),), 1))
        event = queue.next_alert(0)
        self.assertEqual((event.home_team, event.away_team, event.home_score,
                          event.away_score, event.description),
                         ("TOT", "COV", 1, 0, "A Player"))
        self.assertIsNotNone(render_scoring_alert(event))

    def test_score_first_alert_has_no_invented_player(self):
        queue = ScoringAlerts(enabled=True, scope="all")
        observe_soccer_match(queue, match())
        observe_soccer_match(queue, match(score=1))
        event = queue.next_alert(0)
        self.assertEqual(event.description, "")
        self.assertEqual(event.home_score, 1)
        self.assertIsNotNone(render_scoring_alert(event))

    def test_other_sport_event_remains_renderable(self):
        event = ScoreEvent(sport="hockey", league="NHL", game_id="1",
                           event_id="2", team_id="ATL", kind="GOAL")
        self.assertIsNotNone(render_scoring_alert(event))


if __name__ == "__main__":
    unittest.main()
