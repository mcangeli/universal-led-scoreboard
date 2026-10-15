"""Extract optional pitch and play metadata from MLB Stats API live game feeds.

This parser is pure and safe to run against archived game fixtures. The
schedule remains authoritative for score, inning, bases, and game status.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class LivePitchDetails:
    pitch_count: int | None = None
    pitch_speed_mph: float | None = None
    previous_play: str | None = None


def parse_live_pitch_details(payload: dict) -> LivePitchDetails:
    live = payload.get('liveData') or {}
    plays = (live.get('plays') or {}).get('allPlays') or []
    current = (live.get('plays') or {}).get('currentPlay') or {}
    boxscore = live.get('boxscore') or {}
    pitcher_id = ((current.get('matchup') or {}).get('pitcher') or {}).get('id')
    pitch_count = None
    if pitcher_id is not None:
        for side in ('away','home'):
            players = ((boxscore.get('teams') or {}).get(side) or {}).get('players') or {}
            player = players.get('ID'+str(pitcher_id)) or {}
            stats = ((player.get('stats') or {}).get('pitching') or {})
            if isinstance(stats.get('numberOfPitches'),int) and stats['numberOfPitches']>=0:
                pitch_count = stats['numberOfPitches']
                break
    speed = None
    # Current at-bat events are the best source of the most recent pitch.
    events = current.get('playEvents') or []
    for event in reversed(events):
        details = event.get('pitchData') or {}
        value = (details.get('startSpeed'))
        if isinstance(value,(float,int)) and not isinstance(value,bool) and 0<=value<=150:
            speed=float(value)
            break
    previous = None
    # The current at-bat is incomplete, so prefer the last completed play.
    for play in reversed(plays):
        if not (play.get('about') or {}).get('isComplete',False):
            continue
        description = str((play.get('result') or {}).get('description') or '').strip()
        if description:
            previous = description
            break
    return LivePitchDetails(pitch_count,speed,previous)
