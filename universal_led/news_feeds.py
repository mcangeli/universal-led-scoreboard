"""Reusable RSS/Atom headline provider for sports and general news.

URLs are configured by the administrator. Parsing and caching are separate
from matrix rendering and from any particular news organization.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .ticker import TickerItem, normalize_items

ATOM = '{http://www.w3.org/2005/Atom}'


@dataclass(frozen=True)
class NewsSource:
    name: str
    url: str
    category: str = 'news'
    enabled: bool = True
    refresh_seconds: int = 900

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError('News source name is required')
        parsed = urlsplit(self.url)
        if parsed.scheme not in ('http','https') or not parsed.netloc:
            raise ValueError('News source URL must be HTTP(S)')
        if not self.category.strip():
            raise ValueError('News category is required')
        if type(self.enabled) is not bool:
            raise ValueError('enabled must be boolean')
        if type(self.refresh_seconds) is not int or not 60 <= self.refresh_seconds <= 86400:
            raise ValueError('refresh_seconds must be between 60 and 86400')


def parse_news_feed(payload: bytes | str, source: NewsSource,
                    *, max_items: int = 30) -> list[TickerItem]:
    root = ElementTree.fromstring(payload)
    result = []
    if root.tag == ATOM+'feed':
        for entry in root.findall(ATOM+'entry'):
            title = ' '.join((entry.findtext(ATOM+'title') or '').split())
            link = next((item.get('href') for item in entry.findall(ATOM+'link')
                         if item.get('href') and item.get('rel','alternate')=='alternate'),None)
            if title:
                result.append(TickerItem(source.name,title,source.category,url=link))
    else:
        for entry in root.findall('.//channel/item'):
            title = ' '.join((entry.findtext('title') or '').split())
            link = (entry.findtext('link') or '').strip() or None
            if title:
                result.append(TickerItem(source.name,title,source.category,url=link))
    return normalize_items(result,max_items=max_items)


class MultiSourceNewsFeed:
    """Per-source throttling; failures never discard other feeds or cached news."""

    def __init__(self, sources, *, fetch=None, clock=None):
        self.sources = tuple(sources)
        if len({s.name.casefold() for s in self.sources}) != len(self.sources):
            raise ValueError('News source names must be unique')
        self.fetch = fetch or self._fetch
        self.clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._cache = {}
        self._next_refresh = {}
        self.errors = {}

    @staticmethod
    def _fetch(url):
        request = Request(url,headers={'User-Agent':'UniversalLEDScoreboard/0.1 (RSS/Atom reader)'})
        with urlopen(request,timeout=8) as response:
            return response.read(2_000_001)

    def items(self):
        with self._lock:
            now=self.clock()
            combined=[]
            for source in self.sources:
                if not source.enabled:
                    continue
                if now>=self._next_refresh.get(source.name,0):
                    self._next_refresh[source.name]=now+source.refresh_seconds
                    try:
                        payload=self.fetch(source.url)
                        if len(payload)>2_000_000:
                            raise ValueError('Feed exceeds 2 MB size limit')
                        parsed=parse_news_feed(payload,source)
                        if not parsed:
                            raise ValueError('Feed returned no headlines')
                        self._cache[source.name]=parsed
                        self.errors.pop(source.name,None)
                    except (OSError,ValueError,ElementTree.ParseError) as exc:
                        self.errors[source.name]=str(exc)
                combined.extend(self._cache.get(source.name,()))
            return normalize_items(combined)
