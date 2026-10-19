"""League-neutral score-delta observer for cached live game snapshots.

Only positive changes after a baseline generate alerts. Never infer a specific
scoring play from a score delta; label it SCORE unless sport rules permit GOAL.
"""
from .scoring_alerts import ScoreEvent


class ScoreChangeObserver:
    def __init__(self, alerts, sport, league, kind="SCORE"):
        self.alerts = alerts
        self.sport = sport
        self.league = league
        self.kind = kind
        self._previous = {}

    def observe(self, games, *, favorite_teams=()):
        if self.alerts is None:
            return ()
        emitted = []
        for game in games:
            key = str(game.game_id)
            scores = (game.away_score, game.home_score)
            previous = self._previous.get(key)
            self._previous[key] = scores
            if previous is None:
                self.alerts.baseline(self.sport, self.league, key, ())
                continue
            if game.status in ("final", "postponed", "canceled", "cancelled"):
                self.alerts.cancel_game(self.sport, self.league, key)
                continue
            if game.status != "live" or any(type(v) is not int for v in scores + previous):
                continue
            if any(new < old for old, new in zip(previous, scores)):
                continue
            events = tuple(
                ScoreEvent(self.sport, self.league, key,
                           f"score:{team}:{new}", team, self.kind,
                           f"{away} - {home}")
                for team, old, new in (
                    (game.away, previous[0], scores[0]),
                    (game.home, previous[1], scores[1]))
                if new > old
                for away, home in (scores,)
            )
            emitted.extend(self.alerts.observe(
                self.sport, self.league, key, events,
                favorite_teams=favorite_teams))
        return tuple(emitted)
