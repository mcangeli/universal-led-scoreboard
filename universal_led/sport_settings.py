"""Validated, versioned native settings for scoreboard sports and rotation."""
from __future__ import annotations
import json
from pathlib import Path
from .config_store import save_config

SPORTS=('mlb','nba','wnba','nfl','nhl','mls','efl')
DEFAULT_SETTINGS={
    'version':1,
    'active_sport':'mlb',
    'sports':{name:{'enabled':name=='mlb','news_enabled':name=='mlb'} for name in SPORTS},
    'mlb':{'favorite_teams':['ATL'],'mode':'fallback','refresh_seconds':60,'rotation_seconds':12,
           'live_classic_percent':50,'live_matchup_percent':25},
    'nhl':{'favorite_teams':[],'mode':'fallback','refresh_seconds':60,'rotation_seconds':12},
    'nba':{'favorite_teams':[],'mode':'fallback','refresh_seconds':60,'rotation_seconds':12},
    'wnba':{'favorite_teams':[],'mode':'fallback','refresh_seconds':60,'rotation_seconds':12},
    'nfl':{'favorite_teams':[],'mode':'fallback','refresh_seconds':60,'rotation_seconds':12},
    'news':{'rotation_interval':5,'headline_seconds':12,'scroll_chars_per_second':3}
}

def validate_settings(value):
    if not isinstance(value,dict) or not (set(DEFAULT_SETTINGS)-{'news','nhl','nba','wnba','nfl'} <= set(value) <= set(DEFAULT_SETTINGS)):
        raise ValueError('Settings require version, active_sport, sports and mlb')
    value=dict(value,news=dict(DEFAULT_SETTINGS['news']) | value.get('news',{}),
               nhl=dict(DEFAULT_SETTINGS['nhl']) | value.get('nhl',{}),
               nba=dict(DEFAULT_SETTINGS['nba']) | value.get('nba',{}),
               wnba=dict(DEFAULT_SETTINGS['wnba']) | value.get('wnba',{}),
               nfl=dict(DEFAULT_SETTINGS['nfl']) | value.get('nfl',{}))
    if set(value['news'])!=set(DEFAULT_SETTINGS['news']):
        raise ValueError('Invalid news rotation settings')
    for key,minimum,maximum in (('rotation_interval',1,20),('headline_seconds',3,120),('scroll_chars_per_second',1,15)):
        number=value['news'][key]
        if type(number) is not int or not minimum<=number<=maximum:
            raise ValueError('Invalid news setting: '+key)
    if type(value['version']) is not int or value['version']!=1:
        raise ValueError('Unsupported settings version')
    if value['active_sport'] not in SPORTS:
        raise ValueError('Unknown active sport')
    sports=value['sports']
    if isinstance(sports,dict) and 'wnba' not in sports:
        sports=dict(sports,wnba=dict(DEFAULT_SETTINGS['sports']['wnba']))
    if not isinstance(sports,dict) or set(sports)!=set(SPORTS):
        raise ValueError('Invalid sports list')
    sports={name:dict(entry) if isinstance(entry,dict) else entry for name,entry in sports.items()}
    for name,entry in sports.items():
        if not isinstance(entry,dict) or set(entry) not in ({'enabled'},{'enabled','news_enabled'}) or type(entry['enabled']) is not bool:
            raise ValueError('Invalid sport enabled flag: '+name)
        entry.setdefault('news_enabled',name=='mlb')
        if type(entry['news_enabled']) is not bool:
            raise ValueError('Invalid sport news flag: '+name)
    value=dict(value,sports=sports)
    if not sports[value['active_sport']]['enabled']:
        raise ValueError('Active sport must be enabled')
    if value['active_sport'] not in ('mlb','nhl','nba','wnba','nfl'):
        raise ValueError('Only MLB, NHL, NBA, WNBA and NFL are supported by the current rendering engine')
    nhl=value['nhl']
    if not isinstance(nhl,dict) or set(nhl)!=set(DEFAULT_SETTINGS['nhl']):
        raise ValueError('Invalid NHL settings')
    teams=nhl['favorite_teams']
    if (not isinstance(teams,list) or
        any(not isinstance(t,str) or len(t)!=3 or not t.isalpha() or t!=t.upper() for t in teams) or
        len(teams)!=len(set(teams))):
        raise ValueError('Invalid NHL favorite teams')
    if nhl['mode'] not in ('favorite','fallback','all'):
        raise ValueError('Invalid NHL rotation mode')
    for key in ('refresh_seconds','rotation_seconds'):
        number=nhl[key]
        if type(number) not in (int,float) or not 5<=number<=3600:
            raise ValueError('Invalid NHL '+key)

    nba=value['nba']
    if not isinstance(nba,dict) or set(nba)!=set(DEFAULT_SETTINGS['nba']):
        raise ValueError('Invalid NBA settings')
    teams=nba['favorite_teams']
    if (not isinstance(teams,list) or
        any(not isinstance(t,str) or len(t)!=3 or not t.isalpha() or t!=t.upper() for t in teams) or
        len(teams)!=len(set(teams))):
        raise ValueError('Invalid NBA favorite teams')
    if nba['mode'] not in ('favorite','fallback','all'):
        raise ValueError('Invalid NBA rotation mode')
    for key in ('refresh_seconds','rotation_seconds'):
        number=nba[key]
        if type(number) not in (int,float) or not 5<=number<=3600:
            raise ValueError('Invalid NBA '+key)

    wnba=value['wnba']
    if not isinstance(wnba,dict) or set(wnba)!=set(DEFAULT_SETTINGS['wnba']):
        raise ValueError('Invalid WNBA settings')
    teams=wnba['favorite_teams']
    if (not isinstance(teams,list) or
        any(not isinstance(t,str) or len(t)!=3 or not t.isalpha() or t!=t.upper() for t in teams) or
        len(teams)!=len(set(teams))):
        raise ValueError('Invalid WNBA favorite teams')
    if wnba['mode'] not in ('favorite','fallback','all'):
        raise ValueError('Invalid WNBA rotation mode')
    for key in ('refresh_seconds','rotation_seconds'):
        number=wnba[key]
        if type(number) not in (int,float) or not 5<=number<=3600:
            raise ValueError('Invalid WNBA '+key)

    nfl=value['nfl']
    if not isinstance(nfl,dict) or set(nfl)!=set(DEFAULT_SETTINGS['nfl']):
        raise ValueError('Invalid NFL settings')
    teams=nfl['favorite_teams']
    if (not isinstance(teams,list) or
        any(not isinstance(t,str) or len(t)!=3 or not t.isalpha() or t!=t.upper() for t in teams) or
        len(teams)!=len(set(teams))):
        raise ValueError('Invalid NFL favorite teams')
    if nfl['mode'] not in ('favorite','fallback','all'):
        raise ValueError('Invalid NFL rotation mode')
    for key in ('refresh_seconds','rotation_seconds'):
        number=nfl[key]
        if type(number) not in (int,float) or not 5<=number<=3600:
            raise ValueError('Invalid NFL '+key)

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
