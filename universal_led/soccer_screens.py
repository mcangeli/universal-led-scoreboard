"""Compact, dependency-free layout descriptions for 64x32 soccer screens.

The existing matrix renderer can consume these lines with its configured fonts.
Long names are shortened deterministically; no feed data is invented.
"""
from dataclasses import dataclass
import re

from .soccer import SoccerGoal, SoccerMatch
from .soccer_rotation import is_live, FINAL_STATES


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
        footer=_fit(_match_status(match), 12),
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


def _match_status(match: SoccerMatch) -> str:
    status = match.status.strip().lower()
    if status in FINAL_STATES:
        return "FINAL"
    if status in ("pre", "scheduled"):
        return "PRE"
    if status == "halftime":
        return "HT"
    if is_live(match):
        clock = (match.clock or "").strip()
        # ESPN may supply 45\u0027+1\u0027; use conventional 45+1\u0027 on the matrix.
        clock = re.sub(r"^(\d+)'\s*\+\s*(\d+)'?$", lambda m: m.group(1) + "+" + m.group(2) + "'", clock)
        if clock:
            if match.period in (1, 2):
                return f"{match.period}H {clock}"
            return clock
        return "LIVE"
    return match.status.upper()
