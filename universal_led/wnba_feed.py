"""WNBA polling using the shared basketball parser and cache."""
from .nba_feed import NBAFeed, fetch_scores
from .nba_runtime import BackgroundNBAFeed


def fetch_wnba_scores(day, *, timeout=5.0):
    return fetch_scores(day, timeout=timeout, league="wnba")


class WNBAFeed(NBAFeed):
    def __init__(self, *, fetcher=fetch_wnba_scores, refresh_seconds=60, clock=None):
        options = {"fetcher": fetcher, "refresh_seconds": refresh_seconds}
        if clock is not None:
            options["clock"] = clock
        super().__init__(**options)


BackgroundWNBAFeed = BackgroundNBAFeed
