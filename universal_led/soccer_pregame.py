"""Enrich scheduled soccer matches from already-cached standings only."""
from dataclasses import replace


def with_cached_records(match, rows):
    """Fill missing W-D-L values; never overwrite match-feed records."""
    if match.status.strip().lower() not in ("pre", "scheduled"):
        return match
    home = match.home_record
    away = match.away_record
    for row in rows:
        if row.league != match.league:
            continue
        record = f"{row.wins}-{row.draws}-{row.losses}"
        identity = {str(row.team_id).upper()}
        if row.abbreviation:
            identity.add(row.abbreviation.upper())
        if match.home_club_key and match.home_club_key == f"espn:{row.team_id}" and home is None:
            home = record
        elif match.away_club_key and match.away_club_key == f"espn:{row.team_id}" and away is None:
            away = record
        else:
            if home is None and match.home_id.upper() in identity:
                home = record
            if away is None and match.away_id.upper() in identity:
                away = record
    return match if (home, away) == (match.home_record, match.away_record) else replace(
        match, home_record=home, away_record=away)
