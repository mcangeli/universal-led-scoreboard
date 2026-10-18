import unittest
from unittest.mock import patch
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_live_details import MLBLiveDetailsScreen, compact_name
from universal_led.runtime_settings import ConfiguredMLBRenderer


class LiveDetailsScreenTests(unittest.TestCase):
    def test_render_is_64_by_32(self):
        game=BaseballGame(pitcher='Max Fried',batter='Ronald Acuna Jr.',balls=3,strikes=2)
        fb=MLBLiveDetailsScreen(game).render()
        self.assertEqual((fb.width,fb.height),(64,32))
        self.assertTrue(any(pixel!=(0,0,0) for row in fb.pixels for pixel in row))

    def test_unsupported_name_characters_are_safe(self):
        self.assertEqual(compact_name('Jose O\'Neill'),"O'NEILL")

    def test_no_details_does_not_rotate_away_from_classic(self):
        renderer=ConfiguredMLBRenderer.__new__(ConfiguredMLBRenderer)
        import threading
        renderer._lock=threading.Lock()
        renderer._started=100.0
        renderer._settings={'mlb':{'favorite_team':'ATL','mode':'all','rotation_seconds':12}}
        class Feed:
            def games(self):
                return [BaseballGame(status='live',pitcher=None,batter=None,balls=None,strikes=None)]
        renderer.feed=Feed()
        with patch('universal_led.runtime_settings.time.monotonic',return_value=109):
            self.assertEqual(renderer._selection()[1],0)

    def test_live_details_appear_second_half_of_slot(self):
        renderer=ConfiguredMLBRenderer.__new__(ConfiguredMLBRenderer)
        import threading
        renderer._lock=threading.Lock()
        renderer._started=100.0
        renderer._settings={'mlb':{'favorite_team':'ATL','mode':'all','rotation_seconds':12}}
        class Feed:
            def games(self):
                return [BaseballGame(status='live',balls=2,strikes=1)]
        renderer.feed=Feed()
        with patch('universal_led.runtime_settings.time.monotonic',return_value=109):
            self.assertEqual(renderer._selection()[1],3)
        with patch('universal_led.runtime_settings.time.monotonic',return_value=103):
            self.assertEqual(renderer._selection()[1],0)


if __name__=='__main__':
    unittest.main()
