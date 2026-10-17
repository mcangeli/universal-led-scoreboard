"""Soccer background polling and goal event forwarding."""
from .nba_runtime import BackgroundNBAFeed


class BackgroundSoccerFeed(BackgroundNBAFeed):
    """Reuse the proven date-aware background worker for soccer."""

    def __init__(self, feed, *, on_match=None, **kwargs):
        super().__init__(feed, **kwargs)
        self.on_match = on_match

    def refresh_once(self):
        matches = super().refresh_once()
        if self.on_match is not None and self.feed.status()["state"] == "running":
            for match in matches:
                self.on_match(match)
        return matches
