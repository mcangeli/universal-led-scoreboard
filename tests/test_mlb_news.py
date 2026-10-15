import unittest

from universal_led.mlb_news import MLBNewsFeed, parse_mlb_headlines


RSS=b'''<?xml version="1.0"?>
<rss version="2.0"><channel><title>MLB News</title>
<item><title> Braves  win  in extras </title><link>https://www.mlb.com/news/a</link></item>
<item><title>Braves win in extras</title></item>
<item><title>Postseason schedule announced</title><link>https://www.mlb.com/news/b</link></item>
<item><title>  </title></item>
</channel></rss>'''


class MLBNewsTests(unittest.TestCase):
    def test_parse_rss_to_universal_ticker(self):
        items=parse_mlb_headlines(RSS)
        self.assertEqual([i.text for i in items],
                         ['Braves win in extras','Postseason schedule announced'])
        self.assertEqual(items[0].source,'mlb')
        self.assertEqual(items[0].url,'https://www.mlb.com/news/a')

    def test_item_limit(self):
        self.assertEqual(len(parse_mlb_headlines(RSS,max_items=1)),1)

    def test_cached_fetch_is_throttled(self):
        now=[100.0]
        calls=[]
        def fetch():
            calls.append(1)
            return RSS
        feed=MLBNewsFeed(refresh_seconds=60,fetch=fetch,clock=lambda:now[0])
        self.assertEqual(len(feed.items()),2)
        now[0]=120
        self.assertEqual(len(feed.items()),2)
        self.assertEqual(len(calls),1)

    def test_error_preserves_last_good_headlines(self):
        now=[100.0]
        def fetch():
            if now[0]>100:
                raise OSError('offline')
            return RSS
        feed=MLBNewsFeed(refresh_seconds=60,fetch=fetch,clock=lambda:now[0])
        self.assertEqual(len(feed.items()),2)
        now[0]=161
        self.assertEqual(len(feed.items()),2)
        self.assertEqual(feed.last_error,'offline')

    def test_invalid_xml_does_not_crash(self):
        feed=MLBNewsFeed(fetch=lambda:b'<rss>broken')
        self.assertEqual(feed.items(),[])
        self.assertIsNotNone(feed.last_error)


if __name__=='__main__':
    unittest.main()
