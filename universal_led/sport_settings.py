"""Validated, versioned native settings for scoreboard sports and rotation."""
from __future__ import annotations
import json
from pathlib import Path
from .config_store import save_config

SPORTS=('mlb','nba','nfl','nhl','mls','efl')
DEFAULT_SETTINGS={
    'version':1,
    'active_sport':'mlb',
    'sports':{name:{'enabled':name=='mlb'} for name in SPORTS},
    'mlb':{'favorite_team':'ATL','mode':'fallback','refresh_seconds':60,'rotation_seconds':12}
}

def validate_settings(value):
    if not isinstance(value,dict) or set(value)!=set(DEFAULT_SETTINGS):
        raise ValueError('Settings require version, active_sport, sports and mlb')
    if type(value['version']) is not int or value['version']!=1:
        raise ValueError('Unsupported settings version')
    if value['active_sport'] not in SPORTS:
        raise ValueError('Unknown active sport')
    sports=value['sports']
    if not isinstance(sports,dict) or set(sports)!=set(SPORTS):
        raise ValueError('Invalid sports list')
    for name,entry in sports.items():
        if not isinstance(entry,dict) or set(entry)!={'enabled'} or type(entry['enabled']) is not bool:
            raise ValueError('Invalid sport enabled flag: '+name)
    if not sports[value['active_sport']]['enabled']:
        raise ValueError('Active sport must be enabled')
    if value['active_sport']!='mlb':
        raise ValueError('Only MLB is supported by the current rendering engine')
    mlb=value['mlb']
    if not isinstance(mlb,dict) or set(mlb)!=set(DEFAULT_SETTINGS['mlb']):
        raise ValueError('Invalid MLB settings')
    if not isinstance(mlb['favorite_team'],str) or len(mlb['favorite_team'])!=3 or not mlb['favorite_team'].isalpha():
        raise ValueError('Favorite team must be a three-letter abbreviation')
    if mlb['mode'] not in ('favorite','fallback','all'):
        raise ValueError('Invalid rotation mode')
    for key in ('refresh_seconds','rotation_seconds'):
        number=mlb[key]
        if type(number) not in (int,float) or not 1<=number<=3600:
            raise ValueError(key+' must be between 1 and 3600 seconds')
    return json.loads(json.dumps(value))

def load_settings(directory):
    path=Path(directory)/'settings.json'
    if not path.exists():
        return json.loads(json.dumps(DEFAULT_SETTINGS))
    return validate_settings(json.loads(path.read_text(encoding='utf-8')))

def save_settings(directory,value):
    validated=validate_settings(value)
    # Existing storage already provides atomic replace and backup handling.
    save_config(directory,'settings',validated)
    return validated
