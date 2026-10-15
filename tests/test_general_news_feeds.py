import unittest
from universal_led.news_feeds import NewsSource, MultiSourceNewsFeed, parse_news_feed

RSS=b'<rss><channel><item><title>World headline</title><link>https://example.org/1</link></item></channel></rss>'
ATOM=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Technology headline</title><link rel="alternate" href="https://example.net/a"/></entry></feed>'


class GeneralNewsTests(unittest.TestCase):
    def test_rss_general_news(self):
        source=NewsSource('world','https://example.org/rss',category='world')
        item=parse_news_feed(RSS,source)[0]
        self.assertEqual((item.source,item.category,item.text),
                         ('world','world','World headline'))

    def test_atom_general_news(self):
        source=NewsSource('technology','https://example.net/atom',category='technology')
        item=parse_news_feed(ATOM,source)[0]
        self.assertEqual(item.url,'https://example.net/a')

    def test_multiple_sources_with_independent_refresh(self):
        now=[100.]
        calls=[]
        sources=[NewsSource('world','https://example.org/rss',refresh_seconds=60),
                 NewsSource('tech','https://example.net/atom',refresh_seconds=120)]
        def fetch(url):
            calls.append(url)
            return ATOM if 'example.net' in url else RSS
        feed=MultiSourceNewsFeed(sources,fetch=fetch,clock=lambda:now[0])
        self.assertEqual(len(feed.items()),2)
        now[0]=170.
        self.assertEqual(len(feed.items()),2)
        self.assertEqual(len(calls),3)

    def test_failed_feed_does_not_block_other_sources(self):
        sources=[NewsSource('offline','https://example.org/rss'),
                 NewsSource('working','https://example.net/rss')]
        def fetch(url):
            if 'example.org' in url:
                raise OSError('offline')
            return RSS
        feed=MultiSourceNewsFeed(sources,fetch=fetch)
        self.assertEqual([i.source for i in feed.items()],['working'])
        self.assertIn('offline',feed.errors)

    def test_disabled_feed_is_not_fetched(self):
        source=NewsSource('disabled','https://example.org/rss',enabled=False)
        feed=MultiSourceNewsFeed([source],fetch=lambda url:self.fail('unexpected'))
        self.assertEqual(feed.items(),[])

    def test_rejects_invalid_url(self):
        with self.assertRaises(ValueError):
            NewsSource('bad','file:///etc/passwd')


if __name__=='__main__':
    unittest.main()
