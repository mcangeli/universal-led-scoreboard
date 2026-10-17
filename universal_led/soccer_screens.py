"""Compact, dependency-free layout descriptions for 64x32 soccer screens.

The existing matrix renderer can consume these lines with its configured fonts.
Long names are shortened deterministically; no feed data is invented.
"""
from dataclasses import dataclass

from .soccer import SoccerGoal, SoccerMatch


@dataclass(frozen=True)
class SoccerScreen:
    kind: str
    header: str
    line1: str
    line2: str
    footer: str


def _fit(value: str, width: int) -> str:
    value = " ".join(str(value).split())
    if len(value) <= width:
        return value
    return value[:max(0, width - 1)] + "~"


def match_screen(match: SoccerMatch) -> SoccerScreen:
    """Prepare concise lines for a 64x32 game frame."""
    return SoccerScreen(
        kind="match",
        header=_fit(match.league, 6),
        line1=f"{_fit(match.away_id, 5):<5} {match.away_score:>2}",
        line2=f"{_fit(match.home_id, 5):<5} {match.home_score:>2}",
        footer=_fit(match.status.upper(), 12),
    )


def goal_screen(match: SoccerMatch, goal: SoccerGoal) -> SoccerScreen:
    """Show the credited scorer when known, otherwise only the scoring team."""
    scorer = goal.scorer.strip() if goal.scorer else ""
    label = "OWN GOAL" if goal.own_goal else "GOAL!"
    score = f"{match.away_score}-{match.home_score}"
    minute = _fit(goal.minute or "", 6)
    return SoccerScreen(
        kind="goal",
        header=label,
        line1=_fit(scorer or goal.team_id or "GOAL", 16),
        line2=_fit(f"{goal.team_id} {minute}".strip(), 16),
        footer=_fit(f"{score} {match.league}", 16),
    )
