"""Offline NFL news and legacy settings regression tests."""
import copy
import unittest
from universal_led.automatic_news import AutomaticSportsNews
from universal_led.nfl_news import NFLNewsFeed
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class NFLNewsTests(unittest.TestCase):
    def test_rss_headline(self):
        rss = b'<rss><channel><item><title>Falcons prepare for Sunday</title></item></channel></rss>'
        feed = NFLNewsFeed(fetch=lambda url: rss)
        items = feed.items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].source, 'nfl')

    def test_news_toggle(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings['sports']['nfl'].update(enabled=True, news_enabled=True)
        class Provider:
            def items(self):
                return ['NFL headline']
        news = AutomaticSportsNews(providers={'nfl': Provider()})
        self.assertEqual(news.items(settings), ['NFL headline'])
        settings['sports']['nfl']['news_enabled'] = False
        self.assertEqual(news.items(settings), [])

    def test_legacy_settings(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        del settings['sports']['nfl']
        del settings['nfl']
        result = validate_settings(settings)
        self.assertIn('nfl', result['sports'])
        self.assertIn('nfl', result)
        self.assertFalse(result['sports']['nfl']['enabled'])


if __name__ == '__main__':
    unittest.main()
