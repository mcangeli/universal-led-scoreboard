import threading
import unittest
from unittest.mock import patch
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_live_details import MLBLiveDetailsScreen
from universal_led.mlb_previous_play import MLBPreviousPlayScreen, sanitize_play
from universal_led.runtime_settings import ConfiguredMLBRenderer


class PitchDisplayTests(unittest.TestCase):
    def test_pitch_statistics_render(self):
        game=BaseballGame(pitch_count=103,pitch_speed_mph=98.4,balls=2,strikes=1)
        frame=MLBLiveDetailsScreen(game).render()
        self.assertEqual((frame.width,frame.height),(64,32))
        self.assertTrue(any(p!=(0,0,0) for p in frame.pixels[27]))

    def test_previous_play_handles_punctuation(self):
        self.assertEqual(sanitize_play('Single! 2 runs.'),'SINGLE  2 RUNS.')
        game=BaseballGame(previous_play='Runner scores! Extra-base hit.')
        frame=MLBPreviousPlayScreen(game,offset=10).render()
        self.assertEqual((frame.width,frame.height),(64,32))

    def test_previous_play_selection_in_last_quarter(self):
        renderer=ConfiguredMLBRenderer.__new__(ConfiguredMLBRenderer)
        renderer._lock=threading.Lock()
        renderer._started=100.0
        renderer._settings={'mlb':{'favorite_team':'ATL','mode':'all','rotation_seconds':12}}
        class Feed:
            def games(self):
                return [BaseballGame(status='live',pitcher='Max Fried',
                                     previous_play='Single to left')]
        renderer.feed=Feed()
        with patch('universal_led.runtime_settings.time.monotonic',return_value=110):
            self.assertEqual(renderer._selection()[1],4)
        with patch('universal_led.runtime_settings.time.monotonic',return_value=108):
            self.assertEqual(renderer._selection()[1],3)


if __name__=='__main__':
    unittest.main()
