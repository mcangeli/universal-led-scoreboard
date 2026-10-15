import unittest
from universal_led.news_feeds import NewsSource, MultiSourceNewsFeed, parse_news_feed


class CustomRSSIntegrationTests(unittest.TestCase):
    def test_rss_news_titles(self):
        source=NewsSource('AP','https://example.com/ap.xml')
        xml=b'<rss version="2.0"><channel><item><title>AP Top Story</title><link>https://example.com/a</link></item></channel></rss>'
        items=parse_news_feed(xml,source)
        self.assertEqual(items[0].text,'AP Top Story')
        self.assertEqual(items[0].source,'AP')

    def test_atom_news_titles(self):
        source=NewsSource('AP','https://example.com/ap.xml')
        xml=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Breaking News</title><link href="https://example.com/a"/></entry></feed>'
        self.assertEqual(parse_news_feed(xml,source)[0].text,'Breaking News')

    def test_empty_feed_reports_error(self):
        source=NewsSource('AP','https://example.com/ap.xml')
        feed=MultiSourceNewsFeed([source],fetch=lambda url:b'<rss><channel/></rss>')
        self.assertEqual(feed.items(),[])
        self.assertIn('AP',feed.errors)

    def test_failed_source_does_not_block_other_sources(self):
        sources=[NewsSource('Broken','https://example.com/broken'),NewsSource('AP','https://example.com/ap')]
        def fetch(url):
            if 'broken' in url: raise OSError('Unavailable')
            return b'<rss><channel><item><title>AP Works</title></item></channel></rss>'
        feed=MultiSourceNewsFeed(sources,fetch=fetch)
        self.assertEqual([item.text for item in feed.items()],['AP Works'])
        self.assertIn('Broken',feed.errors)

    def test_oversized_feed_is_rejected(self):
        source=NewsSource('AP','https://example.com/ap')
        feed=MultiSourceNewsFeed([source],fetch=lambda url:b' '*2_000_001)
        self.assertEqual(feed.items(),[])
        self.assertIn('AP',feed.errors)


if __name__=='__main__':
    unittest.main()
