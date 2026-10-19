"""Normalize ESPN NBA conference standings without inventing tiebreakers."""
import json
from urllib.request import Request, urlopen

from .standings import Standing

NBA_STANDINGS_URL = 'https://site.api.espn.com/apis/v2/sports/basketball/nba/standings'
NBA_CONFERENCES = ('Eastern', 'Western')


def _stat(stats, *names):
    for stat in stats:
        if isinstance(stat, dict) and (stat.get('name') in names or
                                      stat.get('abbreviation') in names):
            value = stat.get('value')
            return value if value is not None else stat.get('displayValue')
    return None


def _integer(value):
    if type(value) is int and value >= 0:
        return value
    if isinstance(value, (float, str)):
        try:
            number = float(value)
            if number >= 0 and number.is_integer():
                return int(number)
        except ValueError:
            pass
    return None


def parse_nba_standings(payload):
    """Read official provider order from conference entries, not local W/L sorting."""
    if not isinstance(payload, dict) or not isinstance(payload.get('children'), list):
        raise ValueError('Invalid NBA standings response')
    result = []
    for conference in payload['children']:
        if not isinstance(conference, dict):
            continue
        name = conference.get('name', '')
        group = next((value for value in NBA_CONFERENCES if value.lower() in name.lower()), None)
        entries = (conference.get('standings') or {}).get('entries', [])
        if group is None or not isinstance(entries, list):
            continue
        for position, entry in enumerate(entries, 1):
            if not isinstance(entry, dict):
                continue
            team = entry.get('team') or {}
            stats = entry.get('stats') or []
            if not isinstance(team, dict) or not isinstance(stats, list):
                continue
            code = team.get('abbreviation')
            wins = _integer(_stat(stats, 'wins', 'W'))
            losses = _integer(_stat(stats, 'losses', 'L'))
            rank = _integer(_stat(stats, 'playoffSeed', 'rank', 'seed'))
            if rank is None or rank < 1:
                rank = position
            if not isinstance(code, str) or not code.strip() or wins is None or losses is None:
                continue
            games_back = _stat(stats, 'gamesBehind', 'GB')
            if games_back is not None:
                games_back = str(games_back).strip()[:5]
            result.append(Standing(
                league='NBA', group=group, team_id=code.upper(),
                abbreviation=code.upper()[:3], played=wins + losses,
                wins=wins, losses=losses, rank=rank, games_back=games_back))
    if not result:
        raise ValueError('NBA standings response has no conference rows')
    return tuple(result)


def fetch_nba_standings(_league='NBA', *, opener=None, timeout=12):
    opener = opener or urlopen
    request = Request(NBA_STANDINGS_URL, headers={
        'User-Agent': 'UniversalLEDScoreboard/0.7', 'Accept': 'application/json'})
    with opener(request, timeout=timeout) as response:
        return parse_nba_standings(json.load(response))


def fetch_nba_conference(group, *, fetcher=fetch_nba_standings):
    if group not in NBA_CONFERENCES:
        raise ValueError('Unknown NBA conference')
    return tuple(row for row in fetcher('NBA') if row.group == group)
