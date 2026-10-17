"""Stable English club identities and season-scoped division membership.

Club IDs are provider-qualified to avoid conflating ESPN IDs with another API.
Competition membership is a fact about a season, never part of a club ID.
"""
from dataclasses import dataclass

COMPETITIONS = {
    "EPL": "eng.1",
    "CHAMPIONSHIP": "eng.2",
    "LEAGUE_ONE": "eng.3",
    "LEAGUE_TWO": "eng.4",
}


@dataclass(frozen=True)
class Club:
    provider: str
    provider_id: str
    name: str

    def __post_init__(self):
        if not self.provider.strip() or not self.provider_id.strip() or not self.name.strip():
            raise ValueError("Club provider, ID and name are required")

    @property
    def key(self):
        return f"{self.provider.lower()}:{self.provider_id}"


@dataclass(frozen=True)
class Membership:
    club_key: str
    season: str
    competition: str

    def __post_init__(self):
        if not self.club_key or not self.season or self.competition not in COMPETITIONS:
            raise ValueError("Invalid season membership")


class ClubRegistry:
    """Keep favorites separate from division membership, even between seasons."""

    def __init__(self):
        self.clubs = {}
        self.memberships = {}

    def add_club(self, club):
        if not isinstance(club, Club):
            raise TypeError("Expected Club")
        old = self.clubs.get(club.key)
        if old and old.provider != club.provider:
            raise ValueError("Club provider conflict")
        self.clubs[club.key] = club
        return club.key

    def assign(self, membership):
        if not isinstance(membership, Membership):
            raise TypeError("Expected Membership")
        if membership.club_key not in self.clubs:
            raise ValueError("Unknown club")
        self.memberships[(membership.club_key, membership.season)] = membership.competition

    def competition_for(self, club_key, season):
        return self.memberships.get((club_key, season))

    def favorites_in(self, favorites, season, competition):
        if competition not in COMPETITIONS:
            raise ValueError("Unknown competition")
        return tuple(key for key in favorites
                     if self.competition_for(key, season) == competition)
