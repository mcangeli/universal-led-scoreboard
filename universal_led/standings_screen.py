"""Compact four-row English football standings display for 64x32 panels."""
from .display import FONT, Framebuffer

GOLD = (239, 195, 95)
WHITE = (235, 235, 225)
GREEN = (100, 205, 125)


def _safe(value, limit):
    return "".join(ch if ch in FONT else " " for ch in str(value).upper())[:limit]


def render_standings(league, rows, *, offset=0):
    """Draw league label plus three ranked entries; rows are already ordered.

    The caller owns official ordering and page selection. Team IDs are used
    until a provider-qualified abbreviation lookup is available.
    """
    if type(offset) is not int or offset < 0:
        raise ValueError("Invalid standings page offset")
    frame = Framebuffer(64, 32)
    frame.text(_safe(league, 10), 1, 0, GOLD)
    for x in range(64):
        frame.pixel(x, 8, (65, 80, 95))
    for index, standing in enumerate(tuple(rows)[offset:offset + 3]):
        y = 10 + index * 7
        rank = standing.rank if standing.rank is not None else offset + index + 1
        # Columns: position (0-11), team (14-37), points (43-61).
        frame.text(_safe(str(rank), 2), 0, y, GREEN)
        frame.text(_safe(standing.team_id, 4), 14, y, WHITE)
        if standing.points is not None:
            frame.text(_safe(str(standing.points), 3), 43, y, GOLD)
    return frame
