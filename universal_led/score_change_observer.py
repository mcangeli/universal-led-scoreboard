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

    def _should_announce(self, game):
        return True

    def _score_steps(self, key, team, old, new):
        return (new,) if new > old else ()

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
            if game.status != "live" or not self._should_announce(game) or any(type(v) is not int for v in scores + previous):
                continue
            if any(new < old for old, new in zip(previous, scores)):
                continue
            events = tuple(
                ScoreEvent(self.sport, self.league, key,
                           f"score:{team}:{step}", team, self.kind,
                           home_team=game.home, away_team=game.away,
                           home_score=scores[1], away_score=scores[0])
                for team, old, new in (
                    (game.away, previous[0], scores[0]),
                    (game.home, previous[1], scores[1]))
                for step in self._score_steps(key, team, old, new)
            )
            emitted.extend(self.alerts.observe(
                self.sport, self.league, key, events,
                favorite_teams=favorite_teams))
        return tuple(emitted)


class NHLGoalObserver(ScoreChangeObserver):
    """Observe NHL live score changes as team goals, without inventing scorers.

    A first snapshot establishes the baseline; subsequent increases during live
    play generate GOAL alerts through the shared deduplicating queue.
    """

    def __init__(self, alerts):
        super().__init__(alerts, sport="nhl", league="NHL", kind="GOAL")
        self._high_water = {}

    def _score_steps(self, key, team, old, new):
        # A downward provider correction must not replay an old goal when
        # the corrected score subsequently climbs back to its earlier value.
        identity = (key, team)
        high = max(old, self._high_water.get(identity, old))
        self._high_water[identity] = max(high, new)
        return range(high + 1, new + 1)


    def _should_announce(self, game):
        # A legitimate late goal may reach the score endpoint after the
        # clock already switches to intermission. Do not discard that delta.
        # Shootout score changes are not ordinary goal announcements.
        return not getattr(game, "shootout", False)
