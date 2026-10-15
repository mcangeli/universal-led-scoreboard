import tempfile
import unittest
from unittest.mock import patch
from universal_led.runtime_settings import ConfiguredMLBRenderer
from universal_led.time_weather_settings import DEFAULT_TIME_WEATHER,save_time_weather
from universal_led.clock_screen import ClockScreen
from universal_led.mlb_classic import BaseballGame


class Feed:
    def __init__(self,game=None):self.game_value=game
    def games(self):return [self.game_value] if self.game_value else []


class ClockRotationTests(unittest.TestCase):
    def test_clock_opt_in_no_games(self):
        with tempfile.TemporaryDirectory() as directory:
            renderer=ConfiguredMLBRenderer(directory,Feed())
            save_time_weather(directory,dict(DEFAULT_TIME_WEATHER))
            with patch('universal_led.runtime_settings.time.monotonic',return_value=renderer._started):
                frame=renderer.frame()
            self.assertEqual(frame.pixels,ClockScreen().render().pixels)

    def test_live_game_protected(self):
        with tempfile.TemporaryDirectory() as directory:
            renderer=ConfiguredMLBRenderer(directory,Feed(BaseballGame(status='live')))
            save_time_weather(directory,dict(DEFAULT_TIME_WEATHER))
            with patch('universal_led.runtime_settings.time.monotonic',return_value=renderer._started):
                frame=renderer.frame()
            self.assertNotEqual(frame.pixels,ClockScreen().render().pixels)

    def test_clock_can_be_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            renderer=ConfiguredMLBRenderer(directory,Feed())
            settings=dict(DEFAULT_TIME_WEATHER,clock_enabled=False)
            save_time_weather(directory,settings)
            with patch('universal_led.runtime_settings.time.monotonic',return_value=renderer._started):
                frame=renderer.frame()
            self.assertNotEqual(frame.pixels,ClockScreen().render().pixels)


if __name__=='__main__':
    unittest.main()
