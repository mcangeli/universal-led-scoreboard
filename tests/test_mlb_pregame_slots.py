import threading
import unittest
from unittest.mock import patch
from universal_led.mlb_classic import BaseballGame
from universal_led.runtime_settings import ConfiguredMLBRenderer


class Feed:
    def games(self):
        return [
            BaseballGame(away='TBR',home='CLE',status='pregame'),
            BaseballGame(away='MIL',home='LAD',status='pregame'),
        ]


class PregameSlotTests(unittest.TestCase):
    def setUp(self):
        self.renderer=ConfiguredMLBRenderer.__new__(ConfiguredMLBRenderer)
        self.renderer._lock=threading.Lock()
        self.renderer._started=100.0
        self.renderer._settings={'mlb':{'favorite_team':'ATL','mode':'all','rotation_seconds':12}}
        self.renderer.feed=Feed()

    def test_each_game_receives_all_three_pages(self):
        cases=[(100,'TBR',0),(104,'TBR',1),(108,'TBR',2),
               (112,'MIL',0),(116,'MIL',1),(120,'MIL',2),
               (124,'TBR',0)]
        for now,away,page in cases:
            with self.subTest(now=now):
                with patch('universal_led.runtime_settings.time.monotonic',return_value=now):
                    game,actual=self.renderer._selection()
                self.assertEqual((game.away,actual),(away,page))

    def test_legacy_settings_without_interruptions_remain_supported(self):
        self.renderer.feed.games=lambda:[BaseballGame(status='delayed')]
        with patch('universal_led.runtime_settings.time.monotonic',return_value=100):
            game,page=self.renderer._selection()
        self.assertEqual(game.status,'delayed')
        self.assertEqual(page,0)

    def test_missing_external_live_flag_defaults_to_false(self):
        self.renderer.feed.games=lambda:[BaseballGame(status='postponed')]
        self.assertFalse(hasattr(self.renderer,'external_live_games'))
        self.assertEqual(self.renderer._selection()[0].status,'postponed')

    def test_cross_sport_live_suppresses_delayed_mlb(self):
        self.renderer.feed.games=lambda:[BaseballGame(status='delayed'),
                                          BaseballGame(away='MIL',home='LAD',status='final')]
        self.renderer.external_live_games=True
        self.assertEqual(self.renderer._selection()[0].status,'final')

    def test_hide_policy_removes_postponed_mlb(self):
        self.renderer._settings['game_interruptions']={'postponed':'hide'}
        self.renderer.feed.games=lambda:[BaseballGame(status='postponed')]
        self.assertIsNone(self.renderer._selection()[0])

    def test_live_game_does_not_rotate_pregame_pages(self):
        self.renderer.feed.games=lambda:[BaseballGame(status='live')]
        for now in (100,104,108):
            with patch('universal_led.runtime_settings.time.monotonic',return_value=now):
                self.assertEqual(self.renderer._selection()[1],0)


if __name__=='__main__':
    unittest.main()
