"""Shared LED palette management and user color overrides."""
from __future__ import annotations
import json
from pathlib import Path
from .mlb_visual import TEAM_COLORS

RGB = tuple[int,int,int]
DEFAULT_SCOREBOARD = {
    'text': (235,235,225), 'dim': (110,125,140),
    'accent': (239,195,95), 'error': (240,80,70),
    'separator': (28,37,48),
}

def parse_rgb(value) -> RGB:
    if isinstance(value,str):
        value=value.strip()
        if value.startswith('#') and len(value)==7:
            try:
                return tuple(int(value[i:i+2],16) for i in (1,3,5))
            except ValueError:
                pass
        raise ValueError('Color must be #RRGGBB or three RGB channels')
    if isinstance(value,(list,tuple)) and len(value)==3 and all(
        isinstance(x,int) and not isinstance(x,bool) and 0<=x<=255 for x in value
    ):
        return tuple(value)
    raise ValueError('RGB channels must be integers from 0 to 255')

def normalize_team_colors(data: dict) -> dict[str,RGB]:
    if not isinstance(data,dict):
        raise ValueError('Team colors must be an object')
    # Supports direct abbreviation->color, or a team entry with a 'primary' key.
    result={}
    for key,value in data.items():
        if not isinstance(key,str) or len(key)!=3:
            raise ValueError('Team keys must be three-letter abbreviations')
        if isinstance(value,dict):
            if 'primary' not in value:
                raise ValueError(f'{key}: missing primary color')
            value=value['primary']
        result[key.upper()]=parse_rgb(value)
    return result

def normalize_scoreboard_colors(data: dict) -> dict[str,RGB]:
    if not isinstance(data,dict):
        raise ValueError('Scoreboard colors must be an object')
    unknown=set(data)-set(DEFAULT_SCOREBOARD)
    if unknown:
        raise ValueError('Unknown scoreboard color keys: '+', '.join(sorted(unknown)))
    return {key:parse_rgb(value) for key,value in data.items()}

def load_palette(team_file: str | Path | None = None,
                 scoreboard_file: str | Path | None = None):
    teams=dict(TEAM_COLORS)
    scoreboard=dict(DEFAULT_SCOREBOARD)
    if team_file is not None:
        teams.update(normalize_team_colors(json.loads(Path(team_file).read_text(encoding='utf-8'))))
    if scoreboard_file is not None:
        scoreboard.update(normalize_scoreboard_colors(json.loads(Path(scoreboard_file).read_text(encoding='utf-8'))))
    return teams,scoreboard
