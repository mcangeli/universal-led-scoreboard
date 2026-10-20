"""NHL goals arriving at intermission still announce; shootout scores do not."""
import unittest
from types import SimpleNamespace
from universal_led.score_change_observer import NHLGoalObserver, ScoreChangeObserver
from universal_led.scoring_alerts import ScoringAlerts


def game(score, **kwargs):
    return SimpleNamespace(game_id=123,away='BOS',home='NYR',away_score=score,home_score=0,status='live',**kwargs)


class NHLGoalPhaseTests(unittest.TestCase):
    def test_late_goal_at_intermission_is_announced_once(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(0)])
        self.assertEqual(len(observer.observe([game(1,intermission=True)])),1)
        self.assertEqual(observer.observe([game(1,intermission=False)]),())
        self.assertEqual(len(observer.observe([game(2,intermission=False)])),1)

    def test_shootout_score_change_is_not_goal(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(0)])
        self.assertEqual(observer.observe([game(1,shootout=True)]),())
        self.assertIsNone(alerts.next_alert(10))

    def test_goal_first_seen_on_final_snapshot_is_announced_once(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(1)])
        final=game(2)
        final.status='final'
        self.assertEqual(len(observer.observe([final])),1)
        self.assertEqual(alerts.next_alert(0).kind,'GOAL')
        self.assertEqual(observer.observe([final]),())
        self.assertIsNone(alerts.next_alert(8))

    def test_shootout_delta_at_final_is_not_announced(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(1)])
        final=game(2,shootout=True)
        final.status='final'
        self.assertEqual(observer.observe([final]),())
        self.assertIsNone(alerts.next_alert(0))

    def test_final_snapshot_does_not_invent_goal_without_live_baseline(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(1)])
        pregame=game(1)
        pregame.status='pregame'
        observer.observe([pregame])
        final=game(2)
        final.status='final'
        self.assertEqual(observer.observe([final]),())
        self.assertIsNone(alerts.next_alert(0))

    def test_other_sports_still_announce_live_score_changes(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=ScoreChangeObserver(alerts,'nba','NBA')
        observer.observe([game(0)])
        self.assertEqual(len(observer.observe([game(1)])),1)


if __name__=='__main__':
    unittest.main()
