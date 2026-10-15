import tempfile
import unittest
from unittest.mock import patch
from universal_led.news_screen import NewsHeadlineScreen
from universal_led.runtime_settings import ConfiguredMLBRenderer
from universal_led.mlb_classic import BaseballGame
from universal_led.ticker import TickerItem


class StubFeed:
    def __init__(self, game):
        self.game_value = game
    def games(self):
        return [self.game_value] if self.game_value else []


class StubNews:
    def items(self):
        return [TickerItem('MLB','BRAVES WIN SERIES')]


class NewsDisplayTests(unittest.TestCase):
    def test_headline_screen_bounds_and_text(self):
        frame=NewsHeadlineScreen('BRAVES WIN SERIES','MLB').render()
        self.assertEqual((frame.width,frame.height),(64,32))
        self.assertTrue(any(pixel!=(0,0,0) for row in frame.pixels for pixel in row))

    def test_no_games_can_show_cached_news(self):
        with tempfile.TemporaryDirectory() as directory:
            renderer=ConfiguredMLBRenderer(directory,StubFeed(None),news=StubNews())
            frame=renderer.frame()
            self.assertEqual(frame.pixels,NewsHeadlineScreen('BRAVES WIN SERIES','MLB',offset=0).render().pixels)

    def test_live_game_never_replaced_by_news(self):
        with tempfile.TemporaryDirectory() as directory:
            renderer=ConfiguredMLBRenderer(directory,StubFeed(BaseballGame(status='live')),news=StubNews())
            with patch('universal_led.runtime_settings.time.monotonic',return_value=renderer._started+60):
                frame=renderer.frame()
            news=NewsHeadlineScreen('BRAVES WIN SERIES','MLB').render()
            self.assertNotEqual(frame.pixels,news.pixels)


if __name__=='__main__':
    unittest.main()
