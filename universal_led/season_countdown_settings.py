"""Optional shared countdown settings, independent of individual sport schemas."""
import json
from datetime import datetime
from pathlib import Path
from .season_countdown import SPORTS, SeasonMilestone, countdown, should_display

DEFAULT = {'enabled': False, 'sport': 'mlb', 'season': '', 'opening_at': None,
           'target': 'league', 'team': None, 'window': 'offseason', 'within_days': 30}


def validate(value):
    if not isinstance(value, dict) or set(value) != set(DEFAULT):
        raise ValueError('Invalid countdown settings keys')
    if type(value['enabled']) is not bool or value['sport'] not in SPORTS:
        raise ValueError('Invalid countdown enabled or sport')
    if value['target'] not in ('league', 'favorite') or value['window'] not in ('offseason', 'always', 'within_days'):
        raise ValueError('Invalid countdown target or window')
    if type(value['within_days']) is not int or not 1 <= value['within_days'] <= 366:
        raise ValueError('Invalid countdown window days')
    if not isinstance(value['season'], str) or not isinstance(value['team'], (str, type(None))):
        raise ValueError('Invalid countdown season or team')
    opening = value['opening_at']
    if opening is not None:
        if not isinstance(opening, str):
            raise ValueError('Opening date must be an ISO timestamp')
        date = datetime.fromisoformat(opening.replace('Z', '+00:00'))
        SeasonMilestone(value['sport'], value['season'], date, value['target'], value['team'])
    elif value['enabled']:
        raise ValueError('Enabled countdown requires an opening date')
    return dict(value)


def load(directory):
    path = Path(directory) / 'season_countdown.json'
    return validate(json.loads(path.read_text(encoding='utf-8'))) if path.exists() else dict(DEFAULT)


def current(directory, *, now=None, season_active=False, live_game=False):
    settings = load(directory)
    if not settings['enabled'] or settings['opening_at'] is None:
        return None
    event = SeasonMilestone(settings['sport'], settings['season'],
                            datetime.fromisoformat(settings['opening_at'].replace('Z', '+00:00')),
                            settings['target'], settings['team'])
    result = countdown(event, now)
    return result if should_display(result, enabled=True, window=settings['window'],
                                    within_days=settings['within_days'],
                                    season_active=season_active, live_game=live_game) else None
