import unittest
from universal_led.screen_rotation import choose_screen


class ScreenRotationTests(unittest.TestCase):
    def test_every_source_gets_slot(self):
        actual=[choose_screen(i,has_game=True,clock=True,weather=True,news=True) for i in range(8)]
        self.assertEqual(actual,['clock','weather','news','game']*2)

    def test_missing_weather_does_not_leave_gap(self):
        actual=[choose_screen(i,has_game=True,clock=True,weather=False,news=True) for i in range(6)]
        self.assertEqual(actual,['clock','news','game']*2)

    def test_countdown_gets_fair_rotation_slot(self):
        actual=[choose_screen(i,has_game=True,clock=True,weather=True,news=True,countdown=True)
                for i in range(10)]
        self.assertEqual(actual,['clock','weather','news','countdown','game']*2)

    def test_countdown_without_other_feeds(self):
        self.assertEqual(choose_screen(0,has_game=False,clock=False,
                                       weather=False,news=False,countdown=True),'countdown')

    def test_unavailable_countdown_does_not_leave_empty_slot(self):
        actual=[choose_screen(i,has_game=False,clock=True,weather=False,
                              news=True,countdown=False) for i in range(6)]
        self.assertEqual(actual,['clock','news']*3)

    def test_weather_only(self):
        self.assertEqual(choose_screen(20,has_game=False,clock=False,weather=True,news=False),'weather')

    def test_plugins_share_nonlive_rotation(self):
        screens = [choose_screen(i, has_game=False, clock=True, weather=False,
                                 news=False, plugins=('magic_number', 'flightwall'))
                   for i in range(6)]
        self.assertEqual(screens, ['clock', 'plugin:magic_number',
                                   'plugin:flightwall'] * 2)

    def test_global_live_games_suppress_all_plugins(self):
        for i in range(8):
            self.assertEqual(choose_screen(i, has_game=False, clock=True,
                                           weather=True, news=True,
                                           plugins=('magic_number', 'flightwall'),
                                           live_games=True), 'game')

    def test_empty_is_splash(self):
        self.assertEqual(choose_screen(0,has_game=False,clock=False,weather=False,news=False),'splash')


if __name__=='__main__':
    unittest.main()
