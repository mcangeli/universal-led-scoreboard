"""Cached standings adapter for the shared board's idle-time pages."""
import time

from .display import Framebuffer
from .standings import order_standings
from .standings_screen import render_standings


class StandingsRotation:
    """Read cached standings only; never fetch from the frame loop."""

    def __init__(self, caches, *, enabled=False, page_seconds=12,
                 clock=time.monotonic, selected_leagues=None, season_policy=None):
        self.caches = dict(caches)
        self.season_policy = season_policy
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
        # One logical slot per competition/division. Its internal pages share
        # the configured slot duration instead of each consuming a full slot.
        competitions = []
        for league, cache in self.caches.items():
            # The policy is a cached, local-only decision. Never perform
            # schedule/API lookups in the display loop.
            if self.season_policy is not None and not self.season_policy(league):
                continue
            if self.selected_leagues is not None and league not in self.selected_leagues:
                continue
            rows = cache.rows()
            if not rows:
                continue
            groups = {}
            for row in rows:
                groups.setdefault(row.group, []).append(row)
            for group_rows in groups.values():
                if any(row.rank is None for row in group_rows):
                    continue
                ordered = order_standings(group_rows)
                page_size = 5 if ordered[0].league == "MLB" else 3
                pages = tuple((league, ordered, offset)
                              for offset in range(0, len(ordered), page_size))
                if pages:
                    competitions.append(pages)
        return tuple(competitions)

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
        # A slot belongs to one league. Advance through its sections within
        # that same slot (e.g. 20 seconds / 5 sections = 4 seconds each).
        identities = [(group[0][0], group[0][1][0].group) for group in pages]
        if (self._page_identity is not None and self._page_slot == slot
                and self._page_identity in identities):
            index = identities.index(self._page_identity)
        else:
            index = slot % len(pages)
        self._page_identity = identities[index]
        self._page_slot = slot
        league_pages = pages[index]
        elapsed = max(0, self.clock() - self.started)
        within_slot = elapsed % self.page_seconds
        section = min(len(league_pages) - 1,
                      int(within_slot * len(league_pages) / self.page_seconds))
        league, rows, offset = league_pages[section]
        label = (rows[0].group.replace('_', ' ') if rows[0].league == 'MLB'
                 else rows[0].group if rows[0].league in ('NHL', 'NBA', 'NFL', 'MLS') else league)
        return render_standings(label, rows, offset=offset)
