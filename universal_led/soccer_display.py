"""Time-bounded goal announcements for the soccer display rotation."""
from collections import deque
from dataclasses import dataclass

from .soccer import GoalEventTracker, SoccerGoal, SoccerMatch
from .soccer_screens import SoccerScreen, goal_screen, match_screen


@dataclass(frozen=True)
class PendingGoal:
    match: SoccerMatch
    goal: SoccerGoal


class SoccerDisplayController:
    """Queue new goal announcements and return to the match afterward.

    Call update() for each fresh feed snapshot and screen() on each render tick.
    Pass monotonic seconds to screen() to avoid wall-clock adjustments.
    """

    def __init__(self, goal_seconds: float = 8.0):
        if goal_seconds <= 0:
            raise ValueError("goal_seconds must be positive")
        self.goal_seconds = float(goal_seconds)
        self.tracker = GoalEventTracker()
        self._pending: deque[PendingGoal] = deque()
        self._active: PendingGoal | None = None
        self._expires: float | None = None
        self._latest: dict[tuple[str, str], SoccerMatch] = {}

    def update(self, match: SoccerMatch) -> None:
        key = (match.league, match.match_id)
        self._latest[key] = match
        # Goals only merit a celebration while play is underway. Late feed
        # corrections after full time must not interrupt final scores.
        from .soccer_rotation import is_live
        new_events = self.tracker.observe(match)
        # Halftime keeps the match in the live rotation, but feed corrections
        # during the break must not trigger a new goal celebration.
        if is_live(match) and match.status.strip().lower() != "halftime":
            for goal in new_events:
                self._pending.append(PendingGoal(match, goal))
        else:
            self._pending = deque(item for item in self._pending
                                  if (item.match.league, item.match.match_id) != key)
            if self._active is not None and (self._active.match.league, self._active.match.match_id) == key:
                self._active = None
                self._expires = None

    def screen(self, match: SoccerMatch, now: float) -> SoccerScreen:
        """Return a goal screen while active, otherwise the latest match screen."""
        key = (match.league, match.match_id)
        current = self._latest.get(key, match)
        if self._active is not None and self._expires is not None and now >= self._expires:
            self._active = None
            self._expires = None
        if self._active is None:
            for _ in range(len(self._pending)):
                candidate = self._pending.popleft()
                if (candidate.match.league, candidate.match.match_id) == key:
                    self._active = candidate
                    self._expires = now + self.goal_seconds
                    break
                self._pending.append(candidate)
        if self._active is not None and (self._active.match.league, self._active.match.match_id) == key:
            return goal_screen(current, self._active.goal)
        return match_screen(current)
