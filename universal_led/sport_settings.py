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
    'mlb':{'favorite_teams':['ATL'],'mode':'fallback','refresh_seconds':60,'rotation_seconds':12,
           'live_classic_percent':50,'live_matchup_percent':25}
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
    if not isinstance(mlb,dict):
        raise ValueError('Invalid MLB settings')
    # Older settings.json files predate the live-page split. Preserve them.
    legacy_keys=set(DEFAULT_SETTINGS['mlb'])-{'live_classic_percent','live_matchup_percent'}
    current_keys=set(DEFAULT_SETTINGS['mlb'])
    allowed_legacy=(current_keys-{'favorite_teams'})|{'favorite_team'}
    if set(mlb) not in (current_keys,current_keys-{'live_classic_percent','live_matchup_percent'},
                        allowed_legacy,allowed_legacy-{'live_classic_percent','live_matchup_percent'}):
        raise ValueError('Invalid MLB settings')
    mlb=dict(mlb)
    if 'favorite_team' in mlb:
        mlb['favorite_teams']=[mlb.pop('favorite_team')]
    mlb=dict(DEFAULT_SETTINGS['mlb']) | mlb
    value=dict(value,mlb=mlb)
    for key in ('live_classic_percent','live_matchup_percent'):
        if type(mlb[key]) is not int or not 0<=mlb[key]<=100:
            raise ValueError(key+' must be between 0 and 100')
    if mlb['live_classic_percent']<1 or mlb['live_classic_percent']+mlb['live_matchup_percent']>100:
        raise ValueError('Invalid live screen allocation')
    teams=mlb['favorite_teams']
    if (not isinstance(teams,list) or not teams or
        any(not isinstance(t,str) or len(t)!=3 or not t.isalpha() or t!=t.upper() for t in teams) or
        len(teams)!=len(set(teams))):
        raise ValueError('Favorite teams must be a nonempty list of unique three-letter abbreviations')
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
