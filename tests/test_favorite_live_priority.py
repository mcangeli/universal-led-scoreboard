import tempfile
import unittest
from unittest.mock import patch

from universal_led.clock_screen import ClockScreen
from universal_led.mlb_classic import BaseballGame
from universal_led.runtime_settings import ConfiguredMLBRenderer
from universal_led.time_weather_settings import DEFAULT_TIME_WEATHER, save_time_weather


class Feed:
    def __init__(self,games):
        self._games=games
    def games(self):
        return self._games


class FavoriteLivePriorityTests(unittest.TestCase):
    def test_favorite_live_wins_even_when_other_game_is_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            other=BaseballGame(away='NYM',home='PHI',status='live')
            favorite=BaseballGame(away='ATL',home='MIA',status='live')
            renderer=ConfiguredMLBRenderer(directory,Feed([other,favorite]))
            self.assertEqual(renderer.game(),favorite)
            save_time_weather(directory,dict(DEFAULT_TIME_WEATHER))
            with patch('universal_led.runtime_settings.time.monotonic',return_value=renderer._started):
                self.assertNotEqual(renderer.frame().pixels,ClockScreen().render().pixels)

    def test_nonfavorite_live_does_not_block_clock(self):
        with tempfile.TemporaryDirectory() as directory:
            other=BaseballGame(away='NYM',home='PHI',status='live')
            renderer=ConfiguredMLBRenderer(directory,Feed([other]))
            save_time_weather(directory,dict(DEFAULT_TIME_WEATHER))
            with patch('universal_led.runtime_settings.time.monotonic',return_value=renderer._started):
                self.assertEqual(renderer.frame().pixels,ClockScreen().render().pixels)


if __name__=='__main__':
    unittest.main()
