"""Adapt MLB cached runs to the shared scoring queue."""
from types import SimpleNamespace
from .score_change_observer import ScoreChangeObserver


class MLBRunObserver:
    def __init__(self, alerts, favorites=lambda: ()):
        self.observer = ScoreChangeObserver(alerts, "mlb", "MLB", "RUN")
        self.favorites = favorites

    def observe(self, games):
        snapshots = (
            SimpleNamespace(game_id=str(game.game_pk), status=game.status,
                            away=game.away, home=game.home,
                            away_score=game.away_runs, home_score=game.home_runs)
            for game in games if game.game_pk is not None
        )
        return self.observer.observe(snapshots, favorite_teams=self.favorites())
