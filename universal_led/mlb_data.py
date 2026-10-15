"""MLB Stats API schedule adapter, with throttling and offline-safe cache."""
from __future__ import annotations
import json
import threading
import time
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen
from .mlb_classic import BaseballGame

API = 'https://statsapi.mlb.com/api/v1/schedule'

# MLB Stats API schedule responses often omit abbreviation. Use stable team IDs.
TEAM_ABBREVIATIONS = {
    108:'LAA',109:'ARI',110:'BAL',111:'BOS',112:'CHC',113:'CIN',
    114:'CLE',115:'COL',116:'DET',117:'HOU',118:'KCR',119:'LAD',
    120:'WSN',121:'NYM',133:'OAK',134:'PIT',135:'SDP',136:'SEA',
    137:'SFG',138:'STL',139:'TBR',140:'TEX',141:'TOR',142:'MIN',
    143:'PHI',144:'ATL',145:'CWS',146:'MIA',147:'NYY',158:'MIL'
}
TEAM_NAMES = {
    'los angeles dodgers':'LAD','los angeles angels':'LAA',
    'milwaukee brewers':'MIL','new york yankees':'NYY',
    'new york mets':'NYM','san francisco giants':'SFG',
    'san diego padres':'SDP','chicago white sox':'CWS',
    'chicago cubs':'CHC','kansas city royals':'KCR',
    'tampa bay rays':'TBR','washington nationals':'WSN',
    'arizona diamondbacks':'ARI','athletics':'OAK'
}

def team_abbreviation(team):
    """Prefer MLB team ID; accept abbreviations and known full-name fallbacks."""
    raw_id = team.get('id')
    try:
        team_id = int(raw_id)
    except (TypeError, ValueError):
        team_id = None
    if team_id in TEAM_ABBREVIATIONS:
        return TEAM_ABBREVIATIONS[team_id]
    abbreviation = str(team.get('abbreviation') or '').upper()
    if abbreviation:
        return abbreviation[:3]
    name = str(team.get('name') or '').strip()
    return TEAM_NAMES.get(name.lower(),name.upper()[:3] if name else 'UNK')


# MLB Stats API returns UTC dates; using the local date on the Pi is a practical
# default for the preview, with an explicit --date override for other time zones.
def parse_schedule(payload: dict, team: str | None = None) -> list[BaseballGame]:
    games = []
    for day in payload.get('dates', []):
        for item in day.get('games', []):
            teams = item.get('teams') or {}
            away, home = teams.get('away') or {}, teams.get('home') or {}
            def abbr(side):
                obj = side.get('team') or {}
                return team_abbreviation(obj)
            a, h = abbr(away), abbr(home)
            if team and team.upper() not in (a, h):
                continue
            abstract = (item.get('status') or {}).get('abstractGameState', '')
            detailed = (item.get('status') or {}).get('detailedState', '').lower()
            if 'postpon' in detailed:
                status = 'postponed'
            elif 'delay' in detailed or 'suspend' in detailed:
                status = 'delayed'
            else:
                status = 'final' if abstract == 'Final' else 'live' if abstract == 'Live' else 'pregame'
            ls = item.get('linescore') or {}
            offense = ls.get('offense') or {}
            def occupied(key):
                return bool(offense.get(key))
            def stat(side, key):
                return max(0, int(side.get(key, 0) or 0))
            # Hits/errors are supplied by the hydrated linescore teams object.
            ls_teams = ls.get('teams') or {}
            def hits_errors(which, key):
                return max(0,int(((ls_teams.get(which) or {}).get(key)) or 0))
            inning = max(1, int(ls.get('currentInning') or 1))
            def record(side):
                league = side.get('leagueRecord') or {}
                wins, losses = league.get('wins'), league.get('losses')
                return f'{wins}-{losses}' if isinstance(wins,int) and isinstance(losses,int) else None
            def probable(side):
                pitcher = side.get('probablePitcher') or {}
                return str(pitcher.get('fullName') or '').strip() or None
            # Live count and current matchup are present in hydrated linescore.
            # Missing values stay unknown rather than being shown as zero.
            count = ls.get('balls'), ls.get('strikes')
            def optional_count(value, upper):
                try:
                    number = int(value)
                    return number if 0 <= number <= upper else None
                except (TypeError, ValueError):
                    return None
            def person_name(obj):
                return str((obj or {}).get('fullName') or '').strip() or None
            defense = ls.get('defense') or {}
            games.append(BaseballGame(
                away=a, home=h, game_pk=item.get('gamePk'),
                away_runs=stat(away,'score'), home_runs=stat(home,'score'),
                away_hits=hits_errors('away','hits'), home_hits=hits_errors('home','hits'),
                away_errors=hits_errors('away','errors'), home_errors=hits_errors('home','errors'),
                inning=inning,
                inning_half='top' if ls.get('isTopInning',True) else 'bottom',
                outs=min(3,max(0,int(ls.get('outs') or 0))),
                bases=(occupied('first'),occupied('second'),occupied('third')),
                status=status, start_time=item.get('gameDate'),
                away_record=record(away), home_record=record(home),
                away_probable=probable(away), home_probable=probable(home),
                balls=optional_count(count[0],4), strikes=optional_count(count[1],3),
                pitcher=person_name(defense.get('pitcher')),
                batter=person_name(offense.get('batter'))))
    return games

class MLBFeed:
    def __init__(self, team: str | None = 'ATL', date: str | None = None,
                 refresh_seconds: float = 60, fetch=None, clock=None):
        if refresh_seconds <= 0:
            raise ValueError('refresh_seconds must be positive')
        self.team = team.upper() if team else None
        self.date = date
        self.refresh_seconds = refresh_seconds
        self.fetch = fetch or self._fetch
        self.clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._next_refresh = 0.0
        self._games: list[BaseballGame] = []
        self.last_error: str | None = None

    def _fetch(self):
        day = self.date or datetime.now().astimezone().date().isoformat()
        url = API + '?' + urlencode({'sportId':1,'date':day,'hydrate':'linescore,probablePitcher'})
        with urlopen(url,timeout=8) as response:
            return json.load(response)

    def games(self) -> list[BaseballGame]:
        # Single request per interval, even with concurrent browser requests.
        with self._lock:
            now = self.clock()
            if now >= self._next_refresh:
                self._next_refresh = now + self.refresh_seconds
                try:
                    parsed = parse_schedule(self.fetch(), self.team)
                    self._games = parsed
                    self.last_error = None
                except (OSError,ValueError,KeyError,TypeError) as exc:
                    self.last_error = str(exc)
                    # Keep last known good data during network failures.
            return list(self._games)
