"""Cached NHL official headlines using the NHL's public news RSS feed."""
from __future__ import annotations

from .news_feeds import MultiSourceNewsFeed, NewsSource

NHL_NEWS_RSS = 'https://www.nhl.com/news/rss'


class NHLNewsFeed:
    """Reuse the shared RSS parser, cache and network error handling."""

    def __init__(self, *, refresh_seconds=900, fetch=None, clock=None):
        source = NewsSource(name='nhl', url=NHL_NEWS_RSS,
                            category='news', refresh_seconds=int(refresh_seconds))
        self.feed = MultiSourceNewsFeed([source], fetch=fetch, clock=clock)

    def items(self):
        return self.feed.items()

    @property
    def last_error(self):
        return self.feed.errors.get('nhl')
