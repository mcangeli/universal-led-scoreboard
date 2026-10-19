"""Cached standings adapter for the shared board's idle-time pages."""
import time

from .display import Framebuffer
from .standings import order_standings
from .standings_screen import render_standings


class StandingsRotation:
    """Read cached standings only; never fetch from the frame loop."""

    def __init__(self, caches, *, enabled=False, page_seconds=12,
                 clock=time.monotonic, selected_leagues=None):
        self.caches = dict(caches)
        self.clock = clock
        self.started = clock()
        self._page_identity = None
        self.selected_leagues = None if selected_leagues is None else frozenset(selected_leagues)
        self.configure(enabled=enabled, page_seconds=page_seconds)

    def configure(self, *, enabled=False, page_seconds=12, selected_leagues=None):
        if type(enabled) is not bool:
            raise ValueError("Invalid standings enabled flag")
        if type(page_seconds) not in (int, float) or not 3 <= page_seconds <= 3600:
            raise ValueError("Invalid standings page duration")
        if selected_leagues is not None:
            if not isinstance(selected_leagues, (list, tuple, set, frozenset)) or any(
                    not isinstance(name, str) or name not in self.caches for name in selected_leagues):
                raise ValueError('Invalid standings league selection')
            self.selected_leagues = frozenset(selected_leagues)
        changed = (getattr(self, 'enabled', None) != enabled or
                   getattr(self, 'page_seconds', None) != page_seconds)
        self.enabled = enabled
        self.page_seconds = page_seconds
        if changed:
            self.started = self.clock()

    def _pages(self):
        if not self.enabled:
            return ()
        # Interleave competitions by page so a full 20-team league table
        # cannot monopolize the display for several minutes.
        by_league = []
        for league, cache in self.caches.items():
            if self.selected_leagues is not None and league not in self.selected_leagues:
                continue
            rows = cache.rows()
            if not rows:
                continue
            league_pages = []
            groups = {}
            for row in rows:
                groups.setdefault(row.group, []).append(row)
            for group_rows in groups.values():
                # Official ranks are authoritative; never guess standings.
                if any(row.rank is None for row in group_rows):
                    continue
                ordered = order_standings(group_rows)
                for offset in range(0, len(ordered), 3):
                    league_pages.append((league, ordered, offset))
            if league_pages:
                by_league.append(league_pages)
        pages = []
        for index in range(max(map(len, by_league), default=0)):
            for league_pages in by_league:
                if index < len(league_pages):
                    pages.append(league_pages[index])
        return tuple(pages)

    def has_pages(self):
        return bool(self._pages())

    def frame(self):
        slot = int(max(0, self.clock() - self.started) // self.page_seconds)
        return self.frame_for_slot(slot)

    def frame_for_slot(self, slot):
        """Render a logical standings slot, independent of inserted news slots."""
        if type(slot) is not int or slot < 0:
            raise ValueError("Invalid standings slot")
        pages = self._pages()
        if not pages:
            return Framebuffer(64, 32)
        # A refresh can add or remove pages mid-slot. Keep the currently
        # displayed league/page stable until the next scheduled transition.
        identities = [(league, rows[offset].group, offset)
                      for league, rows, offset in pages]
        if self._page_identity is not None and self._page_slot == slot and self._page_identity in identities:
            index = identities.index(self._page_identity)
        else:
            index = slot % len(pages)
        self._page_identity = identities[index]
        self._page_slot = slot
        league, rows, offset = pages[index]
        return render_standings(league, rows, offset=offset)
