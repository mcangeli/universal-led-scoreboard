"""Live sports take priority over supplemental rotation content."""
import unittest
from types import SimpleNamespace
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.screen_rotation import choose_screen


class Fake:
    def __init__(self, sport, status):
        self.sport = sport
        self.status = status
    def game(self):
        return SimpleNamespace(status=self.status)
    def frame(self):
        return self.sport


class LivePriorityTests(unittest.TestCase):
    def test_supplemental_screens_suppressed(self):
        for position in range(10):
            self.assertEqual(choose_screen(position, has_game=True, clock=True,
                             weather=True, news=True, countdown=True, live_games=True), 'game')

    def test_live_sports_only(self):
        now = [0]
        mlb, nhl, nba = Fake('mlb', 'live'), Fake('nhl', 'final'), Fake('nba', 'live')
        router = MultiSportRenderer(mlb, nhl, nba_renderer=nba, clock=lambda: now[0])
        router.configure_rotation(('mlb', 'nhl', 'nba'), interval=5)
        self.assertEqual(router.frame(), 'mlb')
        now[0] = 5
        self.assertEqual(router.frame(), 'nba')
        now[0] = 10
        self.assertEqual(router.frame(), 'mlb')

    def test_return_to_normal_after_live_game(self):
        now = [0]
        mlb, nhl = Fake('mlb', 'live'), Fake('nhl', 'final')
        router = MultiSportRenderer(mlb, nhl, clock=lambda: now[0])
        router.configure_rotation(('mlb', 'nhl'), interval=5)
        self.assertEqual(router.frame(), 'mlb')
        mlb.status = 'final'
        now[0] = 5
        self.assertEqual(router.frame(), 'nhl')


if __name__ == '__main__':
    unittest.main()
