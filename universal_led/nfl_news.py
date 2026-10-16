"""Cached NFL headlines using the shared RSS reader."""
from .news_feeds import MultiSourceNewsFeed, NewsSource

NEWS_RSS = 'https://www.espn.com/espn/rss/nfl/news'


class NFLNewsFeed:
    def __init__(self, *, refresh_seconds=900, fetch=None, clock=None):
        source = NewsSource(name='nfl', url=NEWS_RSS,
                            category='news', refresh_seconds=int(refresh_seconds))
        self.feed = MultiSourceNewsFeed([source], fetch=fetch, clock=clock)

    def items(self):
        return self.feed.items()

    @property
    def last_error(self):
        return self.feed.errors.get('nfl')
