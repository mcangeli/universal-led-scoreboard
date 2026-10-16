"""Basketball news toggles and RSS parsing regression tests."""
import copy
import unittest
from universal_led.automatic_news import AutomaticSportsNews, SUPPORTED_NEWS
from universal_led.sport_settings import DEFAULT_SETTINGS
from universal_led.nba_news import NBANewsFeed
from universal_led.wnba_news import WNBANewsFeed


class Stub:
    def __init__(self, name):
        self.name = name
        self.calls = 0
    def items(self):
        self.calls += 1
        return [self.name]


class BasketballNewsTests(unittest.TestCase):
    def test_supported_leagues(self):
        self.assertIn("nba", SUPPORTED_NEWS)
        self.assertIn("wnba", SUPPORTED_NEWS)

    def test_independent_news_toggles(self):
        nba, wnba = Stub("nba"), Stub("wnba")
        automatic = AutomaticSportsNews(providers={"nba": nba, "wnba": wnba})
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings["sports"]["mlb"]["enabled"] = False
        settings["sports"]["nba"].update(enabled=True, news_enabled=True)
        settings["sports"]["wnba"].update(enabled=True, news_enabled=False)
        self.assertEqual(automatic.items(settings), ["nba"])
        settings["sports"]["wnba"]["news_enabled"] = True
        self.assertEqual(automatic.items(settings), ["nba", "wnba"])

    def test_rss_parsing(self):
        xml = b"<rss><channel><item><title>Basketball headline</title></item></channel></rss>"
        for provider in (NBANewsFeed, WNBANewsFeed):
            feed = provider(fetch=lambda url: xml)
            items = feed.items()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].text, "Basketball headline")


if __name__ == "__main__":
    unittest.main()
