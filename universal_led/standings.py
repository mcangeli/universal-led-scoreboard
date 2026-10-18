"""League-neutral standings records and explicit ranking policies.

Feeds own the official numbers. Ranking rules are league-specific and must
never silently substitute a different sport's tiebreakers.
"""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Standing:
    league: str
    group: str
    team_id: str
    played: int
    wins: int
    losses: int
    draws: int = 0
    points: Optional[int] = None
    goal_difference: Optional[int] = None
    rank: Optional[int] = None

    def __post_init__(self):
        if not self.league or not self.group or not self.team_id:
            raise ValueError("Standing requires league, group and team")
        values = (self.played, self.wins, self.losses, self.draws)
        if any(type(v) is not int or v < 0 for v in values):
            raise ValueError("Standing totals must be nonnegative integers")
        if self.wins + self.losses + self.draws > self.played:
            raise ValueError("Results cannot exceed games played")
        if self.points is not None and type(self.points) is not int:
            raise ValueError("Points must be an integer")
        if self.goal_difference is not None and type(self.goal_difference) is not int:
            raise ValueError("Goal difference must be an integer")
        if self.rank is not None and (type(self.rank) is not int or self.rank < 1):
            raise ValueError("Official rank must be a positive integer")


def order_standings(rows, *, policy="official") -> Tuple[Standing, ...]:
    """Sort within one league/group; preserve input order for unresolved ties.

    'official' requires ranks supplied by the provider. 'football' is a
    provisional points/goal-difference display, not a claim to resolve
    head-to-head or other competition-specific tiebreakers.
    """
    rows = tuple(rows)
    if len({(r.league, r.group) for r in rows}) > 1:
        raise ValueError("Cannot rank different leagues or groups together")
    if policy == "official":
        if any(r.rank is None for r in rows):
            raise ValueError("Official ranking requires provider ranks")
        return tuple(sorted(rows, key=lambda r: r.rank))
    if policy == "football":
        if any(r.points is None or r.goal_difference is None for r in rows):
            raise ValueError("Football ranking requires points and goal difference")
        return tuple(sorted(rows, key=lambda r: (-r.points, -r.goal_difference)))
    raise ValueError("Unknown standings policy")
