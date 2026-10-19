"""Provider-independent season calendar validation.

Network adapters fetch calendars in background; this module never guesses
league dates and is safe to use with explicit provider season boundaries.
"""
from datetime import datetime, timezone

PHASES = frozenset({'regular', 'postseason', 'offseason'})


def parse_season_windows(windows):
    """Normalize provider-supplied UTC-aware [start, end) season windows."""
    if not isinstance(windows, (list, tuple)):
        raise ValueError('Invalid season windows')
    parsed = []
    for item in windows:
        if not isinstance(item, dict) or set(item) != {'phase', 'start', 'end'}:
            raise ValueError('Invalid season window')
        phase = item['phase']
        if phase not in {'regular', 'postseason'}:
            raise ValueError('Invalid season phase')
        try:
            start = datetime.fromisoformat(item['start'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(item['end'].replace('Z', '+00:00'))
        except (AttributeError, TypeError, ValueError) as exc:
            raise ValueError('Invalid season boundary') from exc
        if start.tzinfo is None or end.tzinfo is None or end <= start:
            raise ValueError('Season boundaries must be ordered and timezone-aware')
        parsed.append((phase, start.astimezone(timezone.utc), end.astimezone(timezone.utc)))
    for i, (_, start, end) in enumerate(parsed):
        if any(start < other_end and other_start < end
               for _, other_start, other_end in parsed[:i]):
            raise ValueError('Overlapping season windows')
    return tuple(parsed)


def season_phase(windows, now=None):
    """Return unknown unless a complete calendar supports an offseason claim.

    A calendar without a known coverage interval cannot establish offseason.
    """
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('Current time must be timezone-aware')
    for phase, start, end in windows:
        if start <= now < end:
            return phase
    return 'unknown'
