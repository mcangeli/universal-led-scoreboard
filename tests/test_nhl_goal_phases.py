"""NHL goal alerts ignore intermission and shootout scoreboard changes."""
import unittest
from types import SimpleNamespace
from universal_led.score_change_observer import NHLGoalObserver, ScoreChangeObserver
from universal_led.scoring_alerts import ScoringAlerts


def game(score, **kwargs):
    return SimpleNamespace(game_id=123,away='BOS',home='NYR',away_score=score,home_score=0,status='live',**kwargs)


class NHLGoalPhaseTests(unittest.TestCase):
    def test_intermission_score_change_is_not_announced_later(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(0)])
        self.assertEqual(observer.observe([game(1,intermission=True)]),())
        self.assertEqual(observer.observe([game(1,intermission=False)]),())
        self.assertEqual(len(observer.observe([game(2,intermission=False)])),1)

    def test_shootout_score_change_is_not_goal(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(0)])
        self.assertEqual(observer.observe([game(1,shootout=True)]),())
        self.assertIsNone(alerts.next_alert(10))

    def test_other_sports_still_announce_live_score_changes(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=ScoreChangeObserver(alerts,'nba','NBA')
        observer.observe([game(0)])
        self.assertEqual(len(observer.observe([game(1)])),1)


if __name__=='__main__':
    unittest.main()
