"""Normalize explicitly supplied NBA regular-season boundaries.

The source adapter must provide verified regular-season dates. A schedule of
individual games, preseason fixtures or a guessed October-to-April range is
not sufficient to establish season eligibility.
"""
from datetime import date, timedelta


def parse_nba_season_windows(payload):
    """Accept provider season records with explicit regular-season boundaries."""
    if not isinstance(payload, dict) or not isinstance(payload.get('seasons'), list):
        raise ValueError('Invalid NBA seasons response')
    windows = []
    for season in payload['seasons']:
        if not isinstance(season, dict):
            continue
        first = season.get('regularSeasonStartDate')
        last = season.get('regularSeasonEndDate')
        if not isinstance(first, str) or not isinstance(last, str):
            continue
        try:
            start = date.fromisoformat(first)
            end = date.fromisoformat(last) + timedelta(days=1)
        except ValueError:
            continue
        if end <= start:
            continue
        windows.append({'phase': 'regular',
                        'start': start.isoformat() + 'T00:00:00Z',
                        'end': end.isoformat() + 'T00:00:00Z'})
    if not windows:
        raise ValueError('NBA seasons response has no verified regular-season boundaries')
    return windows
