import copy
import unittest

from universal_led.automatic_news import AutomaticSportsNews, SUPPORTED_NEWS
from universal_led.nhl_news import NHLNewsFeed, NHL_NEWS_RSS
from universal_led.sport_settings import DEFAULT_SETTINGS

RSS=b'<rss><channel><item><title>NHL Playoff Update</title><link>https://www.nhl.com/news/test</link></item></channel></rss>'


class NHLNewsIntegrationTests(unittest.TestCase):
    def test_source_points_to_nhl_com_headlines(self):
        self.assertIn('host=www.nhl.com', NHL_NEWS_RSS)
        self.assertNotIn('www.nhl.com/news/rss', NHL_NEWS_RSS)

    def test_nhl_feed_parses_and_caches(self):
        calls=[]
        def fetch(url):
            calls.append(url)
            return RSS
        now=[100.]
        feed=NHLNewsFeed(fetch=fetch,clock=lambda:now[0])
        self.assertEqual(feed.items()[0].text,'NHL Playoff Update')
        self.assertEqual(feed.items()[0].source,'nhl')
        self.assertEqual(len(calls),1)
        feed.items()
        self.assertEqual(len(calls),1)

    def test_news_switches_are_independent(self):
        class Provider:
            def __init__(self,name):self.name=name
            def items(self):return [self.name]
        automatic=AutomaticSportsNews({'mlb':Provider('mlb'),'nhl':Provider('nhl')})
        settings=copy.deepcopy(DEFAULT_SETTINGS)
        settings['sports']['nhl']['enabled']=True
        settings['sports']['nhl']['news_enabled']=True
        settings['sports']['mlb']['news_enabled']=False
        self.assertEqual(automatic.items(settings),['nhl'])
        settings['sports']['mlb']['news_enabled']=True
        self.assertEqual(automatic.items(settings),['mlb','nhl'])

    def test_nhl_provider_registered(self):
        self.assertIn('nhl',SUPPORTED_NEWS)
        self.assertIsInstance(AutomaticSportsNews().providers['nhl'],NHLNewsFeed)


if __name__=='__main__':
    unittest.main()
