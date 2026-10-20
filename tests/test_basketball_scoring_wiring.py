"""NBA and WNBA scoring events must be wired to background polling."""
import inspect
import unittest
from types import SimpleNamespace
from universal_led import configurator
from universal_led.score_change_observer import BasketballMomentObserver
from universal_led.scoring_alerts import ScoringAlerts


class BasketballScoringWiringTests(unittest.TestCase):
    def test_background_observers_exist_for_both_leagues(self):
        source = inspect.getsource(configurator.main)
        for league in ('nba', 'wnba'):
            self.assertIn(f"{league}_score_observer = BasketballMomentObserver(scoring_alerts, '{league}', '{league.upper()}')", source)
            self.assertIn(f"{league}_score_observer.observe(games, favorite_teams={league}_renderer.favorite_teams)", source)

    def test_ordinary_basket_is_silent_and_lead_change_announces(self):
        alerts = ScoringAlerts(enabled=True, scope='all', seconds=3)
        observer = BasketballMomentObserver(alerts, 'nba', 'NBA')
        def game(away, home):
            return SimpleNamespace(game_id='1', status='live', away='ATL', home='BOS',
                                   away_score=away, home_score=home)
        observer.observe((game(30, 40),))
        observer.observe((game(32, 40),))
        self.assertIsNone(alerts.next_alert(0))
        observer.observe((game(42, 40),))
        event = alerts.next_alert(0)
        self.assertIsNotNone(event)
        self.assertEqual((event.league, event.team_id), ('NBA', 'ATL'))
        observer.observe((game(42, 40),))
        self.assertIsNone(alerts.next_alert(4))


if __name__ == '__main__':
    unittest.main()
