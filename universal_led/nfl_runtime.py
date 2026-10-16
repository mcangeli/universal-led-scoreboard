"""NFL polling and favorite-team selection, sharing basketball's proven worker."""
from .nba_runtime import BackgroundNBAFeed, select_games

class BackgroundNFLFeed(BackgroundNBAFeed):
    """Poll the NFL scoreboard for the configured local day."""
