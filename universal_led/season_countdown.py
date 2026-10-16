"""Sport-independent season milestone and countdown calculations.

No network access or MLB dependencies: schedule adapters supply the target date.
All datetimes must be timezone-aware to avoid off-by-one-day errors.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

SPORTS = ('mlb', 'nba', 'nfl', 'nhl', 'mls', 'efl')
TARGETS = ('league', 'favorite')
WINDOWS = ('offseason', 'always', 'within_days')

@dataclass(frozen=True)
class SeasonMilestone:
    sport: str
    season: str
    starts_at: datetime
    target: Literal['league', 'favorite'] = 'league'
    team: str | None = None

    def __post_init__(self):
        if self.sport not in SPORTS:
            raise ValueError('Unsupported sport')
        if self.target not in TARGETS:
            raise ValueError('Unsupported countdown target')
        if self.starts_at.tzinfo is None or self.starts_at.utcoffset() is None:
            raise ValueError('Opening time must have timezone information')
        if self.target == 'favorite' and not self.team:
            raise ValueError('Favorite-team milestone requires a team')
        if not self.season.strip():
            raise ValueError('Season is required')

@dataclass(frozen=True)
class Countdown:
    milestone: SeasonMilestone
    seconds_remaining: int
    days: int
    hours: int
    minutes: int

def countdown(milestone: SeasonMilestone, now: datetime | None = None) -> Countdown | None:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('Current time must have timezone information')
    # Round up so the display never announces zero before the event starts.
    remaining = (milestone.starts_at - now).total_seconds()
    if remaining <= 0:
        return None
    seconds = int(-(-remaining // 1))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    return Countdown(milestone, seconds, days, hours, minutes)

def should_display(result: Countdown | None, *, enabled: bool,
                   window: str = 'offseason', season_active: bool = False,
                   within_days: int = 30, live_game: bool = False) -> bool:
    if window not in WINDOWS:
        raise ValueError('Unknown countdown display window')
    if not isinstance(within_days, int) or isinstance(within_days, bool) or not 1 <= within_days <= 366:
        raise ValueError('within_days must be 1..366')
    if not enabled or result is None or live_game:
        return False
    if window == 'offseason':
        return not season_active
    if window == 'within_days':
        return result.seconds_remaining <= within_days * 86400
    return True
