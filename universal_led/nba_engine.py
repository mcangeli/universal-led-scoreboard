"""NBA cached-feed to 64x32 frame adapter."""
import time
from .nba_runtime import select_games
from .game_interruptions import InterruptionPolicy, filter_interrupted_games
from .nba_screen import NBAScreen
from .scoring_alerts import ScoreEvent


class ConfiguredNBARenderer:
    def __init__(self, feed, *, favorite_teams=None, mode="fallback",
                 rotation_seconds=12, clock=time.monotonic, scoring_alerts=None, league='NBA'):
        self.feed = feed
        self.scoring_alerts = scoring_alerts
        self.league = league
        self._lead_snapshots = {}
        self.interruption_policy = InterruptionPolicy()
        self.external_live_games = False
        self.clock = clock
        self.timezone_name = "America/New_York"
        self.time_format = "12h"
        self.configure(favorite_teams=favorite_teams, mode=mode,
                       rotation_seconds=rotation_seconds)

    def configure(self, *, favorite_teams=None, mode="fallback", rotation_seconds=12):
        if mode not in ("favorite", "fallback", "all"):
            raise ValueError("Invalid NBA rotation mode")
        if type(rotation_seconds) not in (int, float) or not 1 <= rotation_seconds <= 3600:
            raise ValueError("Invalid NBA rotation duration")
        teams = list(favorite_teams or [])
        if any(not isinstance(t, str) or len(t) != 3 or not t.isalpha() for t in teams):
            raise ValueError("Invalid NBA favorite team")
        self.favorite_teams = [t.upper() for t in teams]
        self.mode = mode
        self.rotation_seconds = rotation_seconds
        self.started = self.clock()

    def _eligible_games(self):
        selected = select_games(self.feed.games(), self.favorite_teams, self.mode)
        return filter_interrupted_games(selected, has_live_games=self.external_live_games,
                                        policy=self.interruption_policy)

    def _observe_lead_changes(self, games):
        """Announce only a direct change from one leader to the other.

        A tie clears the prior leader; the first lead after a tie is not a
        lead change. Repeated polling of the same snapshot is silent.
        """
        for game in games:
            if game.status != 'live' or game.away_score is None or game.home_score is None:
                continue
            leader = (game.away if game.away_score > game.home_score else
                      game.home if game.home_score > game.away_score else None)
            first = game.game_id not in self._lead_snapshots
            previous = self._lead_snapshots.get(game.game_id)
            self._lead_snapshots[game.game_id] = leader
            if first and self.scoring_alerts is not None:
                self.scoring_alerts.baseline(self.league.lower(), self.league, str(game.game_id), ())
            if previous is None or leader is None or previous == leader:
                continue
            if self.scoring_alerts is None:
                continue
            event = ScoreEvent(sport=self.league.lower(), league=self.league,
                               game_id=str(game.game_id),
                               event_id=f"lead:{game.period}:{game.clock}:{game.away_score}:{game.home_score}",
                               team_id=leader, kind="LEAD", description=f"{leader} TAKES LEAD")
            # First observation establishes a baseline; subsequent changes
            # are announced only when the shared opt-in queue is enabled.
            self.scoring_alerts.observe(self.league.lower(), self.league,
                                        str(game.game_id), (event,),
                                        favorite_teams=self.favorite_teams)

    def has_games(self):
        return bool(self._eligible_games())

    def has_live_games(self):
        """Check every eligible cached game, not just the currently selected one."""
        return any(game.status == "live" for game in
                   self._eligible_games())

    def game(self):
        games = self._eligible_games()
        if not games:
            return None
        live = [g for g in games if g.status == "live"]
        if live:
            games = live
        return games[int(max(0, self.clock() - self.started) // self.rotation_seconds) % len(games)]

    def frame(self):
        return NBAScreen(self.game(), timezone_name=self.timezone_name,
                         time_format=self.time_format).render()
