"""League-neutral, opt-in scoring alert queue.

Adapters submit confirmed provider event IDs; no score-difference guesses.
The first observation of each game establishes a baseline.
"""
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreEvent:
    sport: str
    league: str
    game_id: str
    event_id: str
    team_id: str
    kind: str
    description: str = ""
    home_team: str = ""
    away_team: str = ""
    home_score: int | None = None
    away_score: int | None = None

    def __post_init__(self):
        if not all((self.sport, self.league, self.game_id,
                    self.event_id, self.team_id, self.kind)):
            raise ValueError("Scoring events require official identity and team")


class ScoringAlerts:
    """Queue confirmed events; favorites win priority without losing others.

    observe() is called with the complete current event snapshot for a game.
    The first snapshot is a baseline, including after a process restart.
    next_alert() is called from the scheduler with monotonic time.
    """

    def __init__(self, *, enabled=False, scope="favorites", seconds=8):
        self._seen = {}
        self._pending = deque()
        self._active = None
        self._expires = None
        self.configure(enabled=enabled, scope=scope, seconds=seconds)

    def configure(self, *, enabled=False, scope="favorites", seconds=8):
        if type(enabled) is not bool or scope not in ("favorites", "all"):
            raise ValueError("Invalid scoring alert settings")
        if type(seconds) not in (int, float) or not 1 <= seconds <= 60:
            raise ValueError("Invalid scoring alert duration")
        # Switching on starts with a clean announcement queue. Event IDs
        # observed while disabled remain baselined and are never replayed.
        if enabled and not getattr(self, 'enabled', False):
            self._pending.clear()
            self._active = None
            self._expires = None
        self.enabled = enabled
        self.scope = scope
        self.seconds = seconds
        if not enabled:
            self._pending.clear()
            self._active = None
            self._expires = None

    def observe(self, sport, league, game_id, events, *, favorite_teams=()):
        """Accept official events, deduplicate, and enqueue permitted new ones."""
        key = (sport, league, str(game_id))
        events = tuple(events)
        if any((e.sport, e.league, e.game_id) != key for e in events):
            raise ValueError("Scoring event belongs to another game")
        ids = {e.event_id for e in events}
        if key not in self._seen:
            self._seen[key] = ids
            return ()
        seen = self._seen[key]
        new = tuple(e for e in events if e.event_id not in seen)
        seen.update(ids)
        if not self.enabled:
            return ()
        favorites = {str(t).upper() for t in favorite_teams}
        accepted = tuple(e for e in new if self.scope == "all"
                         or e.team_id.upper() in favorites)
        for event in accepted:
            if event.team_id.upper() in favorites:
                # Put favorites ahead of queued nonfavorites, retaining
                # their arrival order; never interrupt an active alert.
                index = next((i for i, queued in enumerate(self._pending)
                              if not queued[0]),
                             len(self._pending))
                self._pending.insert(index, (True, event))
            else:
                self._pending.append((False, event))
        return accepted

    def baseline(self, sport, league, game_id, events):
        """Ingest confirmed IDs without announcing them (halftime/final)."""
        key = (sport, league, str(game_id))
        events = tuple(events)
        if any((e.sport, e.league, e.game_id) != key for e in events):
            raise ValueError("Scoring event belongs to another game")
        self._seen.setdefault(key, set()).update(e.event_id for e in events)
        return ()

    def cancel_game(self, sport, league, game_id):
        """Drop stale announcements when a match enters halftime or finishes."""
        key = (sport, league, str(game_id))
        self._pending = deque((favorite, event) for favorite, event in self._pending
                              if (event.sport, event.league, event.game_id) != key)
        if self._active is not None and (
                self._active.sport, self._active.league, self._active.game_id) == key:
            self._active = None
            self._expires = None

    def next_alert(self, now):
        """Return active event or None; expire and restore rotation naturally."""
        if not self.enabled:
            return None
        if self._active is not None and now >= self._expires:
            self._active = None
            self._expires = None
        if self._active is None and self._pending:
            self._active = self._pending.popleft()[1]
            self._expires = now + self.seconds
        return self._active
