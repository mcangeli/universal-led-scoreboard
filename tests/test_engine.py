import unittest
from universal_led.engine import ScoreboardEngine
from universal_led.screens import MLBDemoScreen, SplashScreen, DemoGame

class EngineTests(unittest.TestCase):
    def test_splash_then_rotation(self):
        now = [0.]
        screens = [MLBDemoScreen(), SplashScreen()]
        engine = ScoreboardEngine(screens, seconds_per_screen=5, splash_seconds=2, clock=lambda: now[0])
        self.assertEqual(engine.current_screen().name, 'splash')
        now[0] = 2.
        self.assertEqual(engine.current_screen().name, 'mlb-demo')
        now[0] = 7.
        self.assertEqual(engine.current_screen().name, 'splash')
        now[0] = 12.
        self.assertEqual(engine.current_screen().name, 'mlb-demo')
    def test_invalid_config(self):
        with self.assertRaises(ValueError):
            ScoreboardEngine([])
        with self.assertRaises(ValueError):
            ScoreboardEngine([SplashScreen()], seconds_per_screen=0)
    def test_mlb_demo_renders(self):
        frame = MLBDemoScreen().render()
        self.assertEqual((frame.width, frame.height), (64,32))
        self.assertTrue(any(any(p != (0,0,0) for p in row) for row in frame.pixels))
    def test_game_fixture_is_offline(self):
        self.assertEqual(DemoGame().home, 'ATL')

if __name__ == '__main__':
    unittest.main()
