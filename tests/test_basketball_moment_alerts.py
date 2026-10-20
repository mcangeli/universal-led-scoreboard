"""NBA and WNBA alerts should highlight moments, not ordinary baskets."""
import unittest
from types import SimpleNamespace
from universal_led.score_change_observer import BasketballMomentObserver
from universal_led.scoring_alerts import ScoringAlerts


def game(away,home,period=2):
    return SimpleNamespace(game_id='1',away='ATL',home='NY',away_score=away,home_score=home,status='live',period=period)


class BasketballMomentTests(unittest.TestCase):
    def setUp(self):
        self.alerts=ScoringAlerts(enabled=True,scope='all')
        self.observer=BasketballMomentObserver(self.alerts,'wnba','WNBA')

    def test_final_keeps_queued_moment(self):
        self.observer.observe([game(10,12)])
        self.observer.observe([game(13,12)])
        final = game(13,12)
        final.status = 'final'
        self.observer.observe([final])
        self.assertEqual(self.alerts.next_alert(0).kind, 'LEAD')
        self.assertIsNone(self.alerts.next_alert(8))

    def test_final_keeps_active_moment(self):
        self.observer.observe([game(10,12)])
        self.observer.observe([game(13,12)])
        self.assertEqual(self.alerts.next_alert(0).kind, 'LEAD')
        final = game(13,12)
        final.status = 'final'
        self.observer.observe([final])
        self.assertEqual(self.alerts.next_alert(7).kind, 'LEAD')
        self.assertIsNone(self.alerts.next_alert(8))

    def test_canceled_game_still_drops_moment(self):
        self.observer.observe([game(10,12)])
        self.observer.observe([game(13,12)])
        canceled = game(13,12)
        canceled.status = 'canceled'
        self.observer.observe([canceled])
        self.assertIsNone(self.alerts.next_alert(0))

    def test_ordinary_baskets_are_silent(self):
        self.observer.observe([game(10,12)])
        self.assertEqual(self.observer.observe([game(12,12)]),())
        self.assertEqual(self.observer.observe([game(14,12)]),())

    def test_direct_lead_change_announced(self):
        self.observer.observe([game(10,12)])
        events=self.observer.observe([game(13,12)])
        self.assertEqual(len(events),1)
        self.assertEqual(events[0].kind,'LEAD')

    def test_late_tie_announced(self):
        self.observer.observe([game(80,82,4)])
        events=self.observer.observe([game(82,82,4)])
        self.assertEqual(len(events),1)
        self.assertEqual(events[0].kind,'LATE TIE')

    def test_eight_unanswered_points_announced_once(self):
        self.observer.observe([game(20,30)])
        self.assertEqual(self.observer.observe([game(24,30)]),())
        events=self.observer.observe([game(28,30)])
        self.assertEqual(len(events),1)
        self.assertEqual(events[0].kind,'RUN')
        self.assertEqual(self.observer.observe([game(28,30)]),())


if __name__=='__main__':
    unittest.main()
