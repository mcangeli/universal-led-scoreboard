"""Non-blocking background headline cache for the display renderer."""
import threading
import time

from .automatic_news import AutomaticSportsNews
from .news_feeds import MultiSourceNewsFeed, NewsSource
from .news_settings import load_news_settings
from .ticker import normalize_items


class BackgroundNews:
    def __init__(self, directory, *, automatic=None, clock=None):
        self.directory = directory
        self.automatic = automatic if automatic is not None else AutomaticSportsNews()
        self.clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._items = []
        self._next = 0.0
        self._running = False
        self._thread = None
        self._custom_feed = None
        self._custom_sources = None

    def start(self, settings_getter):
        if self._running:
            return
        self._running = True
        def worker():
            while self._running:
                if self.clock() >= self._next:
                    self._next = self.clock() + 60
                    try:
                        settings = settings_getter()
                        configured = load_news_settings(self.directory)
                        sources = [NewsSource(**source) for source in configured['sources']]
                        signature = tuple(sources)
                        if signature != self._custom_sources:
                            self._custom_feed = MultiSourceNewsFeed(sources) if sources else None
                            self._custom_sources = signature
                        custom = self._custom_feed.items() if self._custom_feed else []
                        items = normalize_items(self.automatic.items(settings) + custom)
                        with self._lock:
                            self._items = items
                    except (OSError, ValueError, TypeError):
                        pass  # Preserve cached headlines and live-score rendering.
                time.sleep(1)
        self._thread = threading.Thread(target=worker, daemon=True, name='scoreboard-news')
        self._thread.start()

    def items(self):
        with self._lock:
            return list(self._items)

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2)
