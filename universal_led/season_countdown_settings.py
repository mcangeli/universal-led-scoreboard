"""Optional shared countdown settings, independent of individual sport schemas."""
import json
from datetime import datetime
from pathlib import Path
from .season_countdown import SPORTS, SeasonMilestone, countdown, should_display

DEFAULT = {'enabled': False, 'sport': 'mlb', 'season': '', 'opening_at': None,
           'target': 'league', 'team': None, 'window': 'offseason', 'within_days': 30, 'source': 'manual'}


def validate(value):
    if not isinstance(value, dict) or set(value) not in (set(DEFAULT), set(DEFAULT)-{'source'}):
        raise ValueError('Invalid countdown settings keys')
    value = dict(DEFAULT) | value
    if value['source'] not in ('manual', 'automatic'):
        raise ValueError('Invalid countdown date source')
    if value['source'] == 'automatic' and value['sport'] != 'mlb':
        raise ValueError('Automatic opening dates currently support MLB only')
    if value['source'] == 'automatic' and value['enabled'] and (not value['season'].isdigit() or len(value['season']) != 4):
        raise ValueError('Automatic MLB countdown requires a four-digit season')
    if value['source'] == 'automatic' and value['target'] == 'favorite' and value['enabled'] and (not value['team'] or len(value['team']) != 3):
        raise ValueError('Favorite-team countdown requires a three-letter team')
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
    elif value['enabled'] and value['source'] == 'manual':
        raise ValueError('Enabled countdown requires an opening date')
    return dict(value)


def load(directory):
    path = Path(directory) / 'season_countdown.json'
    return validate(json.loads(path.read_text(encoding='utf-8'))) if path.exists() else dict(DEFAULT)


def current(directory, *, now=None, season_active=False, live_game=False, provider=None):
    settings = load(directory)
    if not settings['enabled']:
        return None
    if settings['source'] == 'automatic':
        if provider is None:
            return None
        event = provider.opening(settings['season'], target=settings['target'], team=settings['team'])
        if event is None:
            return None
    else:
        if settings['opening_at'] is None:
            return None
        event = SeasonMilestone(settings['sport'], settings['season'],
                                datetime.fromisoformat(settings['opening_at'].replace('Z', '+00:00')),
                                settings['target'], settings['team'])
    result = countdown(event, now)
    return result if should_display(result, enabled=True, window=settings['window'],
                                    within_days=settings['within_days'],
                                    season_active=season_active, live_game=live_game) else None
