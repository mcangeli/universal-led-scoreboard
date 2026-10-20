"""NHL score corrections and multiple goals between feed refreshes."""
import unittest
from types import SimpleNamespace
from universal_led.score_change_observer import NHLGoalObserver
from universal_led.scoring_alerts import ScoringAlerts


def game(score):
    return SimpleNamespace(game_id=321,away='BOS',home='NYR',away_score=score,home_score=0,status='live')


class NHLGoalCorrectionsTests(unittest.TestCase):
    def test_two_goals_between_polls_get_separate_alerts(self):
        alerts=ScoringAlerts(enabled=True,scope='all',seconds=5)
        observer=NHLGoalObserver(alerts)
        observer.observe([game(0)])
        events=observer.observe([game(2)])
        self.assertEqual([e.event_id for e in events],['score:BOS:1','score:BOS:2'])
        self.assertEqual(alerts.next_alert(10).event_id,'score:BOS:1')
        self.assertEqual(alerts.next_alert(16).event_id,'score:BOS:2')

    def test_correction_and_recovery_do_not_repeat_old_goal(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        observer.observe([game(0)])
        self.assertEqual(len(observer.observe([game(2)])),2)
        self.assertEqual(observer.observe([game(1)]),())
        self.assertEqual(observer.observe([game(2)]),())
        self.assertEqual([e.event_id for e in observer.observe([game(3)])],['score:BOS:3'])

    def test_first_snapshot_never_announces_existing_goals(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        observer=NHLGoalObserver(alerts)
        self.assertEqual(observer.observe([game(3)]),())
        self.assertEqual([e.event_id for e in observer.observe([game(4)])],['score:BOS:4'])


if __name__=='__main__':
    unittest.main()
