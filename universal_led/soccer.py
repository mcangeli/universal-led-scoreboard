"""League-neutral soccer match and goal-event normalization.

Adapters should supply official event IDs and credited scorers when available.
No provider-specific network access belongs in this module.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SoccerGoal:
    event_id: str
    team_id: str
    scorer: Optional[str] = None
    minute: Optional[str] = None
    own_goal: bool = False


@dataclass(frozen=True)
class SoccerMatch:
    match_id: str
    league: str
    home_id: str
    away_id: str
    home_score: int
    away_score: int
    status: str
    goals: tuple[SoccerGoal, ...] = ()


SUPPORTED_LEAGUES = frozenset(("MLS", "NWSL"))


def new_goals(previous: Optional[SoccerMatch], current: SoccerMatch) -> tuple[SoccerGoal, ...]:
    """Return newly observed credited goals, not repeated feed snapshots.

    The first snapshot establishes a baseline to avoid celebrating old goals
    after service startup. Corrected/removed events are not re-announced.
    """
    if current.league not in SUPPORTED_LEAGUES:
        raise ValueError("Unsupported soccer league")
    if previous is None:
        return ()
    if (previous.match_id, previous.league) != (current.match_id, current.league):
        return ()
    seen = {goal.event_id for goal in previous.goals}
    return tuple(goal for goal in current.goals if goal.event_id and goal.event_id not in seen)
