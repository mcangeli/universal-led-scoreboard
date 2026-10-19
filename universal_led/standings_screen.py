"""Readable, compact 64x32 standings pages."""
from .display import FONT, Framebuffer

GOLD = (239, 195, 95)
WHITE = (235, 235, 225)
GREEN = (100, 205, 125)
DIM = (65, 80, 95)


def _safe(value, limit):
    return "".join(ch if ch in FONT else " " for ch in str(value).upper())[:limit]


def render_standings(league, rows, *, offset=0):
    """Three ranked entries with non-overlapping 5x7 glyphs.

    64 pixels allow a two-character rank, three-character club code and
    three-character points total. Avoid four-character club labels because
    their glyphs crowd the points column.
    """
    if type(offset) is not int or offset < 0:
        raise ValueError("Invalid standings page offset")
    frame = Framebuffer(64, 32)
    labels = {"CHAMPIONSHIP": "CHAMP", "LEAGUE_ONE": "LGE 1",
              "LEAGUE_TWO": "LGE 2"}
    frame.text(_safe(labels.get(league, league), 6), 1, 0, GOLD)
    frame.text("PTS", 45, 0, GOLD)
    for x in range(64):
        frame.pixel(x, 8, DIM)

    # Seven-pixel glyphs with a separator pixel between the first two
    # rows. The final row ends at pixel 31, inside the physical panel.
    for index, standing in enumerate(tuple(rows)[offset:offset + 3]):
        y = (10, 18, 25)[index]
        rank = standing.rank if standing.rank is not None else offset + index + 1
        frame.text(_safe(rank, 2), 1, y, GREEN)
        club = _safe(standing.abbreviation or standing.team_id, 3)
        frame.text(club, 17, y, WHITE)
        if standing.points is not None:
            points = _safe(standing.points, 3)
            frame.text(points, 44 + (3 - len(points)) * 6, y, GOLD)
    return frame
