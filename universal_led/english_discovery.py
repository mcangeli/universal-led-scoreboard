"""Extract stable ESPN club identities from English football scoreboard payloads.

This is discovery only. A single match-day schedule cannot establish a full
season roster, and an empty schedule must never erase known memberships.
"""
from collections.abc import Mapping

from .english_football import Club, Membership, COMPETITIONS


def season_for(day):
    """English football season label from a date (July through June)."""
    year = day.year if day.month >= 7 else day.year - 1
    return f"{year}-{(year + 1) % 100:02d}"


def discover_clubs(payload, competition, season):
    """Return (Club, Membership) pairs, deduplicated by ESPN club ID."""
    if competition not in COMPETITIONS:
        raise ValueError("Unknown English football competition")
    if not isinstance(payload, Mapping) or not isinstance(payload.get("events"), list):
        raise ValueError("Expected ESPN events list")
    found = {}
    for event in payload["events"]:
        if not isinstance(event, Mapping):
            continue
        for match in event.get("competitions") or []:
            if not isinstance(match, Mapping):
                continue
            for row in match.get("competitors") or []:
                if not isinstance(row, Mapping):
                    continue
                team = row.get("team")
                if not isinstance(team, Mapping):
                    continue
                team_id = str(team.get("id") or "").strip()
                name = str(team.get("displayName") or team.get("name") or "").strip()
                if not team_id or not name:
                    continue
                club = Club("espn", team_id, name)
                found[club.key] = (club, Membership(club.key, season, competition))
    return tuple(found.values())


def register_discovered(registry, payload, competition, season):
    """Apply discovered clubs to an existing registry; do not delete others."""
    pairs = discover_clubs(payload, competition, season)
    for club, membership in pairs:
        registry.add_club(club)
        registry.assign(membership)
    return len(pairs)
