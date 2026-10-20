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
        self._previous_status = {}

    def _announce_final_delta(self, game, previous_status):
        return False

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
            previous_status = self._previous_status.get(key)
            self._previous[key] = scores
            self._previous_status[key] = game.status
            if previous is None:
                self.alerts.baseline(self.sport, self.league, key, ())
                continue
            if game.status == "final":
                # NHL may report a last regulation/OT goal in the same poll
                # that first reports Final. Other sports remain conservative.
                if not self._announce_final_delta(game, previous_status):
                    self.alerts.finalize_game(self.sport, self.league, key)
                    continue
            if game.status in ("postponed", "canceled", "cancelled"):
                self.alerts.cancel_game(self.sport, self.league, key)
                continue
            if game.status not in ("live", "final") or not self._should_announce(game) or any(type(v) is not int for v in scores + previous):
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

    def _announce_final_delta(self, game, previous_status):
        return previous_status == "live" and not getattr(game, "shootout", False)

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


class BasketballMomentObserver(ScoreChangeObserver):
    """Announce key NBA/WNBA moments rather than every basket.

    A direct lead change, a tie in the fourth quarter or overtime, or an
    eight-point unanswered run qualifies. Polling snapshots never invent
    individual basket events.
    """

    def __init__(self, alerts, sport, league):
        super().__init__(alerts, sport, league, kind="MOMENT")
        self._run = {}

    def observe(self, games, *, favorite_teams=()):
        if self.alerts is None:
            return ()
        emitted = []
        for game in games:
            key = str(game.game_id)
            scores = (game.away_score, game.home_score)
            old = self._previous.get(key)
            self._previous[key] = scores
            if old is None:
                self._run[key] = (0, 0)
                self.alerts.baseline(self.sport, self.league, key, ())
                continue
            if game.status in ("final", "postponed", "canceled", "cancelled"):
                if game.status == "final":
                    # Preserve already detected moments until their display slot.
                    self.alerts.finalize_game(self.sport, self.league, key)
                else:
                    self.alerts.cancel_game(self.sport, self.league, key)
                self._run.pop(key, None)
                continue
            if game.status != "live" or any(type(v) is not int for v in scores + old):
                continue
            if any(new < before for before, new in zip(old, scores)):
                self._run[key] = (0, 0)
                continue
            away_delta, home_delta = scores[0] - old[0], scores[1] - old[1]
            away_run, home_run = self._run.get(key, (0, 0))
            if away_delta and home_delta:
                away_run, home_run = 0, 0
            elif away_delta:
                away_run, home_run = away_run + away_delta, 0
            elif home_delta:
                away_run, home_run = 0, home_run + home_delta
            self._run[key] = (away_run, home_run)
            before = old[0] - old[1]
            after = scores[0] - scores[1]
            moment = None
            team = None
            if before * after < 0:
                moment = "LEAD"
                team = game.away if after > 0 else game.home
            elif before != 0 and after == 0 and (game.period or 0) >= 4:
                moment = "LATE TIE"
                team = game.away if away_delta else game.home
            elif away_run >= 8 and away_delta:
                moment, team = "RUN", game.away
                self._run[key] = (0, home_run)
            elif home_run >= 8 and home_delta:
                moment, team = "RUN", game.home
                self._run[key] = (away_run, 0)
            if moment is None:
                continue
            event = ScoreEvent(self.sport, self.league, key,
                               f"moment:{moment}:{scores[0]}:{scores[1]}",
                               team, moment,
                               home_team=game.home, away_team=game.away,
                               home_score=scores[1], away_score=scores[0])
            emitted.extend(self.alerts.observe(
                self.sport, self.league, key, (event,),
                favorite_teams=favorite_teams))
        return tuple(emitted)
