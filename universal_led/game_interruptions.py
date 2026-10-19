"""Shared policy for delayed, postponed, rescheduled and suspended fixtures.

Providers keep their original status; this module only determines rotation
eligibility. A genuinely live fixture always outranks interruption cards.
"""
from dataclasses import dataclass


STATUS_GROUPS = {
    "delayed": frozenset(("delayed", "delay", "rain_delay", "weather_delay")),
    "postponed": frozenset(("postponed", "ppd")),
    "rescheduled": frozenset(("rescheduled", "reschedule")),
    "suspended": frozenset(("suspended", "susp")),
}


@dataclass(frozen=True)
class InterruptionPolicy:
    delayed: str = "when_no_live"
    postponed: str = "when_no_live"
    rescheduled: str = "when_no_live"
    suspended: str = "when_no_live"

    def __post_init__(self):
        for field in STATUS_GROUPS:
            if getattr(self, field) not in ("hide", "when_no_live", "always"):
                raise ValueError("Invalid interruption policy for " + field)


def interruption_kind(status):
    normalized = str(status or "").strip().lower().replace("-", "_").replace(" ", "_")
    return next((kind for kind, aliases in STATUS_GROUPS.items()
                 if normalized in aliases), None)


def show_interruption(status, *, has_live_games=False, policy=None):
    """Whether a non-live fixture can occupy a rotation slot."""
    kind = interruption_kind(status)
    if kind is None:
        return True
    policy = policy or InterruptionPolicy()
    choice = getattr(policy, kind)
    return choice == "always" or (choice == "when_no_live" and not has_live_games)


def filter_interrupted_games(games, *, has_live_games=False, policy=None):
    """Filter cached provider games without changing order or provider statuses."""
    games = tuple(games)
    live_present = has_live_games or any(getattr(game, "status", None) == "live" for game in games)
    return [game for game in games if show_interruption(
        getattr(game, "status", None), has_live_games=live_present, policy=policy)]
