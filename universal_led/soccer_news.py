"""Cached MLS and NWSL headlines through the shared RSS reader.

Google News RSS searches provide league-specific coverage without requiring
an API key. Feed failures are isolated from the game display.
"""
from urllib.parse import quote

from .news_feeds import MultiSourceNewsFeed, NewsSource

LEAGUE_QUERIES = {
    "mls": '"Major League Soccer" OR MLS soccer',
    "nwsl": '"National Women\'s Soccer League" OR NWSL',
}


class SoccerNewsFeed:
    def __init__(self, league, *, refresh_seconds=900, fetch=None, clock=None):
        league = str(league).lower()
        if league not in LEAGUE_QUERIES:
            raise ValueError("Unsupported soccer news league")
        self.league = league
        url = "https://news.google.com/rss/search?q=" + quote(LEAGUE_QUERIES[league]) + "&hl=en-US&gl=US&ceid=US:en"
        source = NewsSource(name=league, url=url, category="news",
                            refresh_seconds=int(refresh_seconds))
        self.feed = MultiSourceNewsFeed([source], fetch=fetch, clock=clock)

    def items(self):
        return self.feed.items()

    @property
    def last_error(self):
        return self.feed.errors.get(self.league)
