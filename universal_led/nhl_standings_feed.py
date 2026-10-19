"""Normalize official NHL standings without importing the archived LED project's API.

NHL standings use regulation losses and overtime losses separately. Standing.draws
holds OTL only for compatibility with the shared standings model; NHL rendering
must label this field OTL, never draws.
"""
from __future__ import annotations

from .standings import Standing


def parse_nhl_standings(payload):
    """Return official division-ranked NHL rows from a standings/now payload."""
    if not isinstance(payload, dict) or not isinstance(payload.get("standings"), list):
        raise ValueError("Invalid NHL standings response")
    rows = []
    for item in payload["standings"]:
        if not isinstance(item, dict):
            continue
        division = item.get("divisionName")
        if isinstance(division, dict):
            division = division.get("default")
        abbreviation = item.get("teamAbbrev")
        if isinstance(abbreviation, dict):
            abbreviation = abbreviation.get("default")
        rank = item.get("divisionSequence")
        wins = item.get("wins")
        losses = item.get("losses")
        overtime_losses = item.get("otLosses")
        played = item.get("gamesPlayed")
        points = item.get("points")
        if (not isinstance(division, str) or not division.strip()
                or not isinstance(abbreviation, str) or not abbreviation.strip()
                or any(type(value) is not int or value < 0
                       for value in (rank, wins, losses, overtime_losses, played, points))
                or rank < 1):
            continue
        rows.append(Standing(
            league="NHL", group=division.strip(), team_id=abbreviation.strip().upper(),
            abbreviation=abbreviation.strip().upper()[:3],
            played=played, wins=wins, losses=losses, draws=overtime_losses,
            points=points, rank=rank))
    return tuple(rows)
