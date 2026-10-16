"""MLB opening-day schedule adapter for the shared season milestone model.

The caller controls fetching and caching. This module never guesses an opening date.
"""
from datetime import datetime
from .mlb_data import TEAM_ABBREVIATIONS
from .season_countdown import SeasonMilestone

def from_schedule(payload: dict, season: int | str, *, target: str = 'league',
                  team: str | None = None) -> SeasonMilestone | None:
    """Return earliest scheduled regular-season game, or None if unavailable.

    Pass a full-season MLB Stats API schedule response with gameType=R.
    A team-specific target filters by the requested three-letter abbreviation.
    """
    if target not in ('league', 'favorite'):
        raise ValueError('Unknown opening-day target')
    if target == 'favorite' and (not isinstance(team, str) or len(team) != 3):
        raise ValueError('Favorite target requires a three-letter team code')
    candidates = []
    for day in payload.get('dates', []):
        for game in day.get('games', []):
            if game.get('gameType') != 'R':
                continue
            if target == 'favorite':
                participants = set()
                for side in ('away', 'home'):
                    obj = ((game.get('teams') or {}).get(side) or {}).get('team') or {}
                    participants.add(TEAM_ABBREVIATIONS.get(obj.get('id'), str(obj.get('abbreviation') or '').upper()))
                if team.upper() not in participants:
                    continue
            raw = game.get('gameDate')
            if not raw:
                continue
            try:
                start = datetime.fromisoformat(raw.replace('Z', '+00:00'))
            except (TypeError, ValueError):
                continue
            if start.tzinfo is None or start.utcoffset() is None:
                continue
            candidates.append(start)
    if not candidates:
        return None
    return SeasonMilestone('mlb', str(season), min(candidates),
                           target=target, team=team.upper() if target == 'favorite' else None)
