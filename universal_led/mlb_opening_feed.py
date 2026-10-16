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
        self.last_error = None

    @staticmethod
    def _fetch(season):
        query = urlencode({'sportId': 1, 'startDate': f'{season}-01-01',
                           'endDate': f'{season}-12-31', 'gameType': 'R'})
        with urlopen(API + '?' + query, timeout=12) as response:
            return json.load(response)

    def opening(self, season, *, target='league', team=None):
        year = int(season)
        if year < 1876 or year > 9999:
            raise ValueError('Invalid MLB season')
        if target not in ('league', 'favorite'):
            raise ValueError('Invalid countdown target')
        if target == 'favorite' and (not isinstance(team, str) or len(team) != 3):
            raise ValueError('Favorite target requires a three-letter team')
        key = (year, target, team.upper() if team else None)
        with self._lock:
            now = self.clock()
            if now >= self._next_refresh.get(year, 0):
                self._next_refresh[year] = now + self.refresh_seconds
                try:
                    payload = self.fetch(year)
                    if not isinstance(payload, dict):
                        raise ValueError('Invalid schedule response')
                    self._cache[year] = payload
                    self.last_error = None
                except (OSError, ValueError, TypeError, KeyError) as exc:
                    self.last_error = str(exc)
            payload = self._cache.get(year)
            if payload is None:
                return None
            return from_schedule(payload, year, target=target, team=team)
