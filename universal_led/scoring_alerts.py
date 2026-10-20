"""League-neutral, opt-in scoring alert queue.

Adapters submit confirmed provider event IDs; no score-difference guesses.
The first observation of each game establishes a baseline.
"""
from collections import deque
from dataclasses import asdict, dataclass
from functools import wraps
from threading import RLock


def synchronized(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapped


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
    MAX_PENDING = 16
    MAX_AGE_SECONDS = 180

    """Queue confirmed events; favorites win priority without losing others.

    observe() is called with the complete current event snapshot for a game.
    The first snapshot is a baseline, including after a process restart.
    next_alert() is called from the scheduler with monotonic time.
    """

    def __init__(self, *, enabled=False, scope="favorites", seconds=8):
        self._lock = RLock()
        self._queued_at = {}
        self._clock = None
        self.on_queue_transition = None
        self._seen = {}
        self._pending = deque()
        self._active = None
        self._active_favorite = False
        self._expires = None
        self.configure(enabled=enabled, scope=scope, seconds=seconds)

    @synchronized
    def set_clock(self, clock):
        """Enable monotonic queue aging using the renderer scheduler clock."""
        self._clock = clock

    @synchronized
    def configure(self, *, enabled=False, scope="favorites", seconds=8):
        if type(enabled) is not bool or scope not in ("favorites", "all"):
            raise ValueError("Invalid scoring alert settings")
        if type(seconds) not in (int, float) or not 1 <= seconds <= 60:
            raise ValueError("Invalid scoring alert duration")
        # Switching on starts with a clean announcement queue. Event IDs
        # observed while disabled remain baselined and are never replayed.
        if enabled and not getattr(self, 'enabled', False):
            self._pending.clear()
            self._queued_at.clear()
            self._active = None
            self._expires = None
        self.enabled = enabled
        self.scope = scope
        self.seconds = seconds
        if not enabled:
            self._pending.clear()
            self._queued_at.clear()
            self._active = None
            self._expires = None

    @synchronized
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
            if self._clock is not None:
                self._queued_at[event] = self._clock()
            if event.team_id.upper() in favorites:
                # Put favorites ahead of queued nonfavorites, retaining
                # their arrival order; never interrupt an active alert.
                index = next((i for i, queued in enumerate(self._pending)
                              if not queued[0]),
                             len(self._pending))
                self._pending.insert(index, (True, event))
            else:
                self._pending.append((False, event))
            # Bound the backlog to avoid showing very old scores after a
            # burst across leagues. Evict oldest nonfavorite first.
            if len(self._pending) > self.MAX_PENDING:
                index = next((i for i, (favorite, _) in enumerate(self._pending)
                              if not favorite), 0)
                dropped = self._pending[index][1]
                del self._pending[index]
                self._queued_at.pop(dropped, None)
        return accepted

    @synchronized
    def export_pending(self, *, now_monotonic, now_epoch):
        """Serialize only queued, not active, alerts with restart-safe UTC ages."""
        rows = []
        for favorite, event in self._pending:
            queued = self._queued_at.get(event)
            if queued is None:
                continue
            age = max(0, now_monotonic - queued)
            if age <= self.MAX_AGE_SECONDS:
                rows.append({"favorite": favorite, "event": asdict(event),
                             "queued_epoch": now_epoch - age})
        return {"version": 1, "pending": rows}

    @synchronized
    def import_pending(self, snapshot, *, now_monotonic, now_epoch):
        """Restore fresh pending events; reject malformed or future timestamps.

        Caller must supply a trusted snapshot and should import before polling.
        Never restore already-active alerts, which may have been displayed.
        """
        if not self.enabled or not isinstance(snapshot, dict) or snapshot.get("version") != 1:
            return 0
        rows = snapshot.get("pending")
        if not isinstance(rows, list):
            return 0
        restored = 0
        for row in rows[:self.MAX_PENDING]:
            if not isinstance(row, dict) or type(row.get("favorite")) is not bool:
                continue
            stamp = row.get("queued_epoch")
            if type(stamp) not in (int, float) or not 0 <= now_epoch - stamp <= self.MAX_AGE_SECONDS:
                continue
            try:
                event = ScoreEvent(**row["event"])
            except (KeyError, TypeError, ValueError):
                continue
            key = (event.sport, event.league, event.game_id)
            self._seen.setdefault(key, set()).add(event.event_id)
            if event == self._active or any(existing == event for _, existing in self._pending):
                continue
            self._pending.append((row["favorite"], event))
            self._queued_at[event] = now_monotonic - (now_epoch - stamp)
            restored += 1
        return restored

    @synchronized
    def baseline(self, sport, league, game_id, events):
        """Ingest confirmed IDs without announcing them (halftime/final)."""
        key = (sport, league, str(game_id))
        events = tuple(events)
        if any((e.sport, e.league, e.game_id) != key for e in events):
            raise ValueError("Scoring event belongs to another game")
        self._seen.setdefault(key, set()).update(e.event_id for e in events)
        return ()

    @synchronized
    def finalize_game(self, sport, league, game_id):
        """Keep already detected scoring events eligible after final status.

        A final transition must not erase a goal or score notification that
        has not yet had its scheduled display slot.
        """
        return None

    @synchronized
    def cancel_game(self, sport, league, game_id):
        """Drop stale announcements when a match enters halftime or finishes."""
        key = (sport, league, str(game_id))
        self._pending = deque((favorite, event) for favorite, event in self._pending
                              if (event.sport, event.league, event.game_id) != key)
        retained = {event for _, event in self._pending}
        self._queued_at = {event: stamp for event, stamp in self._queued_at.items()
                           if event in retained}
        if self._active is not None and (
                self._active.sport, self._active.league, self._active.game_id) == key:
            self._queued_at.pop(self._active, None)
            self._active = None
            self._expires = None

    @synchronized
    def render_failed(self, event):
        """Retry an alert whose frame could not be rendered.

        Preserve its priority and reset the presentation timer rather than
        treating failed rendering as time spent visibly displaying an alert.
        """
        if self._active is not None and self._active == event:
            self._expires = None
            self._pending.appendleft((self._active_favorite, event))
            self._active = None
            if self.on_queue_transition is not None:
                self.on_queue_transition()

    @synchronized
    def rendered(self, event, now):
        """Start the alert duration after its first successful frame render.

        This acknowledges software rendering, not physical matrix delivery.
        """
        if self.enabled and self._active == event and self._expires is None:
            self._expires = now + self.seconds

    @synchronized
    def next_alert(self, now, *, defer_start=False):
        """Return active event; optionally defer its timer until rendered()."""
        if not self.enabled:
            return None
        if self._active is not None and self._expires is not None and now >= self._expires:
            self._queued_at.pop(self._active, None)
            self._active = None
            self._expires = None
        if self._clock is not None:
            cutoff = self._clock() - self.MAX_AGE_SECONDS
            self._pending = deque((fav, event) for fav, event in self._pending
                                  if self._queued_at.get(event, self._clock()) >= cutoff)
            # Keep the active event's original age for failed-render retries.
            retained = {event for _, event in self._pending}
            if self._active is not None:
                retained.add(self._active)
            self._queued_at = {event: stamp for event, stamp in self._queued_at.items()
                               if event in retained}
        if self._active is None and self._pending:
            self._active_favorite, self._active = self._pending.popleft()
            self._expires = None if defer_start else now + self.seconds
            if self.on_queue_transition is not None:
                self.on_queue_transition()
        return self._active
