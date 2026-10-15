"""MLB headline provider using the public MLB RSS feed.

Network fetching is injectable so parser and cache behavior can be tested
without internet access or a running Raspberry Pi.
"""
from __future__ import annotations

import threading
import time
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .ticker import TickerItem, normalize_items

MLB_NEWS_RSS = 'https://www.mlb.com/feeds/news/rss.xml'


def parse_mlb_headlines(xml: bytes | str, *, max_items: int = 20) -> list[TickerItem]:
    """Convert RSS headlines to universal ticker items, ignoring empty titles."""
    root = ElementTree.fromstring(xml)
    items = []
    for entry in root.findall('.//channel/item'):
        title = ' '.join((entry.findtext('title') or '').split())
        if not title:
            continue
        link = (entry.findtext('link') or '').strip() or None
        items.append(TickerItem(source='mlb', text=title, category='news',
                                url=link))
    return normalize_items(items, max_items=max_items)


class MLBNewsFeed:
    """Cached, throttled headline provider. Keep good headlines on errors."""

    def __init__(self, *, refresh_seconds: float = 900, fetch=None, clock=None):
        if refresh_seconds <= 0:
            raise ValueError('refresh_seconds must be positive')
        self.refresh_seconds = refresh_seconds
        self.fetch = fetch or self._fetch
        self.clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._next_refresh = 0.0
        self._items: list[TickerItem] = []
        self.last_error: str | None = None

    @staticmethod
    def _fetch():
        request = Request(MLB_NEWS_RSS, headers={
            'User-Agent': 'UniversalLEDScoreboard/0.1 (RSS reader)'})
        with urlopen(request, timeout=8) as response:
            return response.read()

    def items(self) -> list[TickerItem]:
        with self._lock:
            now = self.clock()
            if now >= self._next_refresh:
                self._next_refresh = now + self.refresh_seconds
                try:
                    self._items = parse_mlb_headlines(self.fetch())
                    self.last_error = None
                except (OSError, ValueError, ElementTree.ParseError) as exc:
                    self.last_error = str(exc)
            return list(self._items)
