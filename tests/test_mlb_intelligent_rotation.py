import threading
import unittest
from unittest.mock import patch
from universal_led.mlb_classic import BaseballGame
from universal_led.runtime_settings import ConfiguredMLBRenderer


def renderer_for(game):
    renderer=ConfiguredMLBRenderer.__new__(ConfiguredMLBRenderer)
    renderer._lock=threading.Lock()
    renderer._started=100.0
    renderer._settings={'mlb':{'favorite_team':'ATL','mode':'all',
                               'rotation_seconds':20,'live_classic_percent':50,
                               'live_matchup_percent':25}}
    class Feed:
        def games(self):
            return [game]
    renderer.feed=Feed()
    return renderer


def selected_at(renderer,seconds):
    with patch('universal_led.runtime_settings.time.monotonic',
               return_value=100.0+seconds):
        return renderer._selection()[1]


class MLBIntelligentRotationTests(unittest.TestCase):
    def test_no_supplemental_data_stays_classic(self):
        renderer=renderer_for(BaseballGame(status='live'))
        self.assertEqual([selected_at(renderer,t) for t in (0,10,15,19)],
                         [0,0,0,0])

    def test_missing_play_expands_matchup(self):
        renderer=renderer_for(BaseballGame(status='live',pitcher='Max Fried'))
        self.assertEqual(selected_at(renderer,12),0)
        self.assertEqual(selected_at(renderer,15),3)
        self.assertEqual(selected_at(renderer,19),3)

    def test_missing_matchup_expands_play(self):
        renderer=renderer_for(BaseballGame(status='live',previous_play='Fly out'))
        self.assertEqual(selected_at(renderer,12),0)
        self.assertEqual(selected_at(renderer,15),4)

    def test_pitch_count_alone_qualifies_for_matchup(self):
        renderer=renderer_for(BaseballGame(status='live',pitch_count=42))
        self.assertEqual(selected_at(renderer,18),3)

    def test_whitespace_play_does_not_qualify(self):
        renderer=renderer_for(BaseballGame(status='live',previous_play='   '))
        self.assertEqual(selected_at(renderer,19),0)


if __name__=='__main__':
    unittest.main()
