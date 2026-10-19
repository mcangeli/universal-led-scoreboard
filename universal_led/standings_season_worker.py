"""Background season calendar refresh, isolated from the LED render loop."""
from __future__ import annotations

from datetime import datetime, timezone
from threading import Event, Lock, Thread
import time

from .standings_season_calendar import parse_season_windows, season_phase
from .standings_season_status import StandingsSeasonStatus


class SeasonCalendarWorker:
    """Fetcher returns provider-supplied windows for a competition.

    An empty or invalid response is not evidence that the season has ended.
    """
    def __init__(self, competition, fetcher, status: StandingsSeasonStatus,
                 *, refresh_seconds=21600, clock=None):
        if not callable(fetcher) or not isinstance(competition, str) or not competition:
            raise ValueError('Invalid season calendar provider')
        if type(refresh_seconds) not in (int, float) or not 60 <= refresh_seconds <= 86400:
            raise ValueError('Invalid season refresh interval')
        self.competition = competition
        self.fetcher = fetcher
        self.status = status
        self.refresh_seconds = refresh_seconds
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self._stop = Event()
        self._thread = None
        self._lock = Lock()
        self._windows = ()
        self.last_error = None

    def refresh(self):
        try:
            windows = parse_season_windows(self.fetcher(self.competition))
            if not windows:
                raise ValueError('Season calendar has no verified windows')
            phase = season_phase(windows, self.clock())
            with self._lock:
                self._windows = windows
                self.last_error = None
            if phase == 'unknown':
                self.status.invalidate(self.competition)
            else:
                self.status.update(self.competition, phase)
            return phase
        except Exception as exc:
            with self._lock:
                self.last_error = str(exc)
            return 'unknown'

    def tick(self):
        """Reevaluate cached boundaries without contacting the provider."""
        with self._lock:
            windows = self._windows
        if not windows:
            return 'unknown'
        phase = season_phase(windows, self.clock())
        if phase == 'unknown':
            self.status.invalidate(self.competition)
        else:
            self.status.update(self.competition, phase)
        return phase

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._run, daemon=True,
                              name='season-' + self.competition)
        self._thread.start()

    def _run(self):
        next_refresh = 0.0
        while not self._stop.is_set():
            now = time.monotonic()
            if now >= next_refresh:
                self.refresh()
                next_refresh = time.monotonic() + self.refresh_seconds
            else:
                self.tick()
            self._stop.wait(min(60, max(1, next_refresh - time.monotonic())))

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=3)
            self._thread = None
