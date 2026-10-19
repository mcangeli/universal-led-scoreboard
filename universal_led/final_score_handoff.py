"""One-time final-score handoff scheduling independent of sport renderers."""
from collections import deque


class FinalScoreHandoff:
    """Remember newly finished games and grant each one display slot.

    A game's first observed state is only a baseline. Final transitions queue
    once, in arrival order; an unrendered final remains pending. Rendering
    adapters are responsible for drawing the actual final-score frame.
    """

    def __init__(self, *, slots=1):
        if type(slots) is not int or slots not in (1, 2, 3):
            raise ValueError("Final handoff slots must be 1, 2, or 3")
        self.slots = slots
        self._statuses = {}
        self._pending = deque()
        self._queued = set()
        self._active = None
        self._remaining = 0

    def observe(self, sport, games, *, id_getter, status_getter=lambda game: game.status):
        for game in games:
            game_id = id_getter(game)
            if game_id is None:
                continue
            key = (sport, str(game_id))
            status = status_getter(game)
            previous = self._statuses.get(key)
            self._statuses[key] = status
            if status == "final" and previous is not None and previous != "final":
                if key not in self._queued:
                    self._pending.append((key, game))
                    self._queued.add(key)

    def next(self):
        """Reserve the next final; caller must acknowledge actual display."""
        if self._active is None and self._pending:
            self._active = self._pending.popleft()
            self._remaining = self.slots
        return self._active

    def displayed(self):
        """Count one completed display slot, not one frame refresh."""
        if self._active is None:
            return
        self._remaining -= 1
        if self._remaining <= 0:
            self._queued.discard(self._active[0])
            self._active = None

    def cancel(self, sport, game_id):
        key = (sport, str(game_id))
        self._pending = deque(item for item in self._pending if item[0] != key)
        self._queued.discard(key)
        if self._active is not None and self._active[0] == key:
            self._active = None
            self._remaining = 0
