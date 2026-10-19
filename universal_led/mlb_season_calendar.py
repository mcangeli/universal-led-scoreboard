"""MLB StatsAPI season boundaries for background standings eligibility."""
import json
from datetime import date, timedelta
from urllib.parse import urlencode
from urllib.request import urlopen

API = 'https://statsapi.mlb.com/api/v1/seasons'


def parse_mlb_season_windows(payload):
    """Use official regular-season and postseason dates, not game-cache ages."""
    seasons = payload.get('seasons')
    if not isinstance(seasons, list):
        raise ValueError('Invalid MLB seasons response')
    windows = []
    for item in seasons:
        if not isinstance(item, dict):
            continue
        regular_start = item.get('regularSeasonStartDate')
        regular_end = item.get('regularSeasonEndDate')
        postseason_end = item.get('postSeasonEndDate')
        if not all(isinstance(value, str) and value
                   for value in (regular_start, regular_end)):
            continue
        try:
            start = date.fromisoformat(regular_start)
            end = date.fromisoformat(regular_end) + timedelta(days=1)
            if end <= start:
                continue
            windows.append({'phase': 'regular',
                            'start': start.isoformat() + 'T00:00:00Z',
                            'end': end.isoformat() + 'T00:00:00Z'})
            if isinstance(postseason_end, str) and postseason_end:
                post_end = date.fromisoformat(postseason_end) + timedelta(days=1)
                if post_end > end:
                    windows.append({'phase': 'postseason',
                                    'start': end.isoformat() + 'T00:00:00Z',
                                    'end': post_end.isoformat() + 'T00:00:00Z'})
        except ValueError:
            continue
    if not windows:
        raise ValueError('MLB seasons response has no usable boundaries')
    return windows


def fetch_mlb_season_windows(_competition, *, year=None, opener=None, timeout=8):
    """Request season dates once per background refresh, never per frame."""
    if year is None:
        year = date.today().year
    if type(year) is not int or not 2000 <= year <= 2100:
        raise ValueError('Invalid MLB season year')
    if opener is None:
        opener = urlopen
    url = API + '?' + urlencode({'sportId': 1, 'season': year})
    with opener(url, timeout=timeout) as response:
        return parse_mlb_season_windows(json.load(response))
