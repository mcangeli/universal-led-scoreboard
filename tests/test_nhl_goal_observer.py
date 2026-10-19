"""NHL goal observation uses the shared live scoring queue."""
import unittest
from types import SimpleNamespace
from universal_led.score_change_observer import NHLGoalObserver
from universal_led.scoring_alerts import ScoringAlerts


def game(away, home, status='live'):
    return SimpleNamespace(game_id=42, away='BOS', home='NYR', away_score=away, home_score=home, status=status)


class NHLGoalObserverTests(unittest.TestCase):
    def test_live_goal_after_baseline_is_announced(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        self.assertEqual(observer.observe([game(0,0)]), ())
        emitted=observer.observe([game(1,0)])
        self.assertEqual(len(emitted),1)
        self.assertEqual((emitted[0].sport,emitted[0].league,emitted[0].kind,emitted[0].team_id),('nhl','NHL','GOAL','BOS'))

    def test_same_score_does_not_repeat_goal(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(0,0)])
        observer.observe([game(1,0)])
        self.assertEqual(observer.observe([game(1,0)]),())

    def test_favorite_scope_filters_other_team(self):
        alerts=ScoringAlerts(enabled=True,scope='favorites')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(0,0)],favorite_teams=('BOS',))
        self.assertEqual(observer.observe([game(0,1)],favorite_teams=('BOS',)),())
        self.assertEqual(len(observer.observe([game(1,1)],favorite_teams=('BOS',))),1)


if __name__=='__main__':
    unittest.main()
