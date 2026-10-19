"""NHL official Stats API season windows for background standings gating."""
import json
from datetime import date, timedelta
from urllib.request import urlopen

API = 'https://api.nhle.com/stats/rest/en/season?limit=-1'


def parse_nhl_season_windows(payload, *, today=None):
    """Select a season spanning the current year, never guess NHL dates."""
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        raise ValueError('Invalid NHL seasons response')
    today = today or date.today()
    windows = []
    for season in payload['data']:
        if not isinstance(season, dict):
            continue
        season_id = season.get('id')
        if type(season_id) is not int or season_id not in (
                (today.year - 1) * 10000 + today.year,
                today.year * 10000 + today.year + 1):
            continue
        first = season.get('regularSeasonStartDate')
        last = season.get('regularSeasonEndDate')
        if not isinstance(first, str) or not isinstance(last, str):
            continue
        try:
            start = date.fromisoformat(first[:10])
            end = date.fromisoformat(last[:10]) + timedelta(days=1)
        except ValueError:
            continue
        if end <= start:
            continue
        windows.append({'phase': 'regular', 'start': start.isoformat() + 'T00:00:00Z',
                        'end': end.isoformat() + 'T00:00:00Z'})
    if not windows:
        raise ValueError('NHL seasons response has no verified regular-season dates')
    return windows


def fetch_nhl_season_windows(_competition, *, opener=None, timeout=8):
    if opener is None:
        opener = urlopen
    with opener(API, timeout=timeout) as response:
        return parse_nhl_season_windows(json.load(response))
