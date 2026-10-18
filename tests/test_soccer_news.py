import unittest

from universal_led.automatic_news import AutomaticSportsNews, SUPPORTED_NEWS
from universal_led.soccer_news import SoccerNewsFeed
from universal_led.sport_settings import DEFAULT_SETTINGS


class SoccerNewsTests(unittest.TestCase):
    def test_leagues_registered(self):
        self.assertIn("mls", SUPPORTED_NEWS)
        self.assertIn("nwsl", SUPPORTED_NEWS)

    def test_league_specific_rss_queries(self):
        mls = SoccerNewsFeed("mls")
        nwsl = SoccerNewsFeed("nwsl")
        self.assertIn("Major%20League%20Soccer", mls.feed.sources[0].url)
        self.assertIn("National%20Women", nwsl.feed.sources[0].url)
        self.assertNotEqual(mls.feed.sources[0].url, nwsl.feed.sources[0].url)

    def test_rss_parses_headlines_for_both_leagues(self):
        xml = b"<rss><channel><item><title>League update</title><link>https://example.org/story</link></item></channel></rss>"
        for league in ("mls", "nwsl"):
            provider = SoccerNewsFeed(league, fetch=lambda url: xml, clock=lambda: 100)
            items = provider.items()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].source, league)

    def test_english_and_efl_are_distinct_sources(self):
        for league in ("english", "efl"):
            self.assertIn(league, SUPPORTED_NEWS)
        premier = SoccerNewsFeed("english")
        efl = SoccerNewsFeed("efl")
        self.assertNotEqual(premier.feed.sources[0].url, efl.feed.sources[0].url)
        self.assertIn("Championship", efl.feed.sources[0].url)

    def test_efl_news_respects_enable_flags(self):
        class Stub:
            def items(self):
                return ["EFL headline"]
        settings = {"sports": {k: dict(v) for k, v in DEFAULT_SETTINGS["sports"].items()}}
        providers = AutomaticSportsNews(providers={"efl": Stub()})
        self.assertEqual(providers.items(settings), [])
        settings["sports"]["efl"] = {"enabled": True, "news_enabled": True}
        self.assertEqual(providers.items(settings), ["EFL headline"])

    def test_sport_flags_gate_automatic_soccer_news(self):
        class Stub:
            def __init__(self, league):
                self.league = league
            def items(self):
                return [self.league]
        settings = {"sports": {k: dict(v) for k, v in DEFAULT_SETTINGS["sports"].items()}}
        settings["sports"]["mls"] = {"enabled": True, "news_enabled": True}
        settings["sports"]["nwsl"] = {"enabled": True, "news_enabled": False}
        providers = AutomaticSportsNews(providers={"mls": Stub("mls"), "nwsl": Stub("nwsl")})
        self.assertEqual(providers.items(settings), ["mls"])
        settings["sports"]["nwsl"]["news_enabled"] = True
        self.assertEqual(providers.items(settings), ["mls", "nwsl"])


if __name__ == "__main__":
    unittest.main()
