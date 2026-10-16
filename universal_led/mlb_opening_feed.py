"""Cached MLB season-opening schedule lookup.

Runs outside the framebuffer renderer. Failed refreshes retain last good data.
The caller may inject a fetcher for deterministic tests.
"""
import json
import threading
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

from .mlb_opening_day import from_schedule

API = 'https://statsapi.mlb.com/api/v1/schedule'

class MLBOpeningDayFeed:
    def __init__(self, refresh_seconds=21600, fetch=None, clock=None):
        if refresh_seconds < 60:
            raise ValueError('Opening-day refresh interval must be at least 60 seconds')
        self.refresh_seconds = refresh_seconds
        self.fetch = fetch or self._fetch
        self.clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._cache = {}
        self._next_refresh = {}
        self._refreshing = set()
        self.last_error = None
        self._last_success = {}

    @staticmethod
    def _fetch(season):
        query = urlencode({'sportId': 1, 'startDate': f'{season}-01-01',
                           'endDate': f'{season}-12-31', 'gameType': 'R'})
        with urlopen(API + '?' + query, timeout=12) as response:
            return json.load(response)

    def _refresh(self, year):
        try:
            payload = self.fetch(year)
            if not isinstance(payload, dict):
                raise ValueError('Invalid schedule response')
        except (OSError, ValueError, TypeError, KeyError) as exc:
            with self._lock:
                self.last_error = str(exc)
        else:
            with self._lock:
                self._cache[year] = payload
                self._last_success[year] = datetime.now(timezone.utc).isoformat()
                self.last_error = None

    def status(self, season):
        """Snapshot for the dashboard; never performs network I/O."""
        year = int(season)
        with self._lock:
            return {'available': year in self._cache,
                    'refreshing': year in self._refreshing,
                    'error': self.last_error,
                    'last_success': self._last_success.get(year)}

    def opening(self, season, *, target='league', team=None):
        year = int(season)
        if year < 1876 or year > 9999:
            raise ValueError('Invalid MLB season')
        if target not in ('league', 'favorite'):
            raise ValueError('Invalid countdown target')
        if target == 'favorite' and (not isinstance(team, str) or len(team) != 3):
            raise ValueError('Favorite target requires a three-letter team')
        with self._lock:
            now = self.clock()
            if now >= self._next_refresh.get(year, 0) and year not in self._refreshing:
                self._next_refresh[year] = now + self.refresh_seconds
                self._refreshing.add(year)
                def background():
                    try:
                        self._refresh(year)
                    finally:
                        with self._lock:
                            self._refreshing.discard(year)
                threading.Thread(target=background, daemon=True,
                                 name=f'mlb-opening-{year}').start()
            payload = self._cache.get(year)
        if payload is None:
            return None
        return from_schedule(payload, year, target=target, team=team)
