import unittest
from universal_led.screen_rotation import choose_screen


class ScreenRotationTests(unittest.TestCase):
    def test_every_source_gets_slot(self):
        actual=[choose_screen(i,has_game=True,clock=True,weather=True,news=True) for i in range(8)]
        self.assertEqual(actual,['clock','weather','news','game']*2)

    def test_missing_weather_does_not_leave_gap(self):
        actual=[choose_screen(i,has_game=True,clock=True,weather=False,news=True) for i in range(6)]
        self.assertEqual(actual,['clock','news','game']*2)

    def test_weather_only(self):
        self.assertEqual(choose_screen(20,has_game=False,clock=False,weather=True,news=False),'weather')

    def test_empty_is_splash(self):
        self.assertEqual(choose_screen(0,has_game=False,clock=False,weather=False,news=False),'splash')


if __name__=='__main__':
    unittest.main()
