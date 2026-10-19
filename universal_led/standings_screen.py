"""Compact 64x32 standings with sport-specific row density."""
from .display import Framebuffer

GOLD = (239, 195, 95)
WHITE = (235, 235, 225)
GREEN = (100, 205, 125)
DIM = (65, 80, 95)

# Three pixels wide, five high; one blank pixel between glyphs.
TINY = {
    "A": ("010", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "C": ("011", "100", "100", "100", "011"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("011", "100", "101", "101", "011"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "J": ("001", "001", "001", "101", "010"),
    "K": ("101", "101", "110", "101", "101"),
    "L": ("100", "100", "100", "100", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "N": ("101", "111", "111", "111", "101"),
    "O": ("010", "101", "101", "101", "010"),
    "P": ("110", "101", "110", "100", "100"),
    "Q": ("010", "101", "101", "111", "011"),
    "R": ("110", "101", "110", "101", "101"),
    "S": ("011", "100", "010", "001", "110"),
    "T": ("111", "010", "010", "010", "010"),
    "U": ("101", "101", "101", "101", "111"),
    "V": ("101", "101", "101", "101", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "X": ("101", "101", "010", "101", "101"),
    "Y": ("101", "101", "010", "010", "010"),
    "Z": ("111", "001", "010", "100", "111"),
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("110", "001", "010", "100", "111"),
    "3": ("110", "001", "010", "001", "110"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "110", "001", "110"),
    "6": ("011", "100", "110", "101", "010"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("010", "101", "010", "101", "010"),
    "9": ("010", "101", "011", "001", "110"),
    " ": ("000",) * 5,
}


def _tiny_text(frame, value, x, y, color, limit):
    for index, char in enumerate(str(value).upper()[:limit]):
        glyph = TINY.get(char, TINY[" "])
        for dy, bits in enumerate(glyph):
            for dx, bit in enumerate(bits):
                if bit == "1":
                    frame.pixel(x + index * 4 + dx, y + dy, color)


def _mlb_text(frame, value, x, y, color, limit):
    """Four-pixel-tall glyphs leave a full blank scanline between teams."""
    for index, char in enumerate(str(value).upper()[:limit]):
        glyph = TINY.get(char, TINY[" "])
        # Compress the five-pixel font without changing character width.
        for dy, source_row in enumerate((0, 1, 2, 4)):
            for dx, bit in enumerate(glyph[source_row]):
                if bit == "1":
                    frame.pixel(x + index * 4 + dx, y + dy, color)


def render_standings(league, rows, *, offset=0):
    """Display five MLB rows or three football rows without collisions."""
    if type(offset) is not int or offset < 0:
        raise ValueError("Invalid standings page offset")
    frame = Framebuffer(64, 32)
    labels = {"CHAMPIONSHIP": "CHAMP", "LEAGUE_ONE": "LGE 1",
              "LEAGUE_TWO": "LGE 2"}
    _tiny_text(frame, labels.get(league, league), 1, 1, GOLD, 9)
    is_mlb = bool(rows) and rows[0].league == "MLB"
    if is_mlb:
        _tiny_text(frame, "W", 48, 1, GOLD, 1)
        _tiny_text(frame, "L", 60, 1, GOLD, 1)
    else:
        _tiny_text(frame, "PTS", 49, 1, GOLD, 3)
    for x in range(64):
        frame.pixel(x, 6 if is_mlb else 8, DIM)
    page_size = 5 if is_mlb else 3
    for index, standing in enumerate(tuple(rows)[offset:offset + page_size]):
        y = (7 + index * 5) if is_mlb else (11 + index * 7)
        rank = standing.rank if standing.rank is not None else offset + index + 1
        if is_mlb:
            # Five compact 3x5 rows fit below the six-pixel header.
            _mlb_text(frame, str(rank), 1, y, GREEN, 1)
            _mlb_text(frame, standing.abbreviation or standing.team_id, 11, y, WHITE, 3)
        else:
            _tiny_text(frame, str(rank).rjust(2), 1, y, GREEN, 2)
            _tiny_text(frame, standing.abbreviation or standing.team_id, 15, y, WHITE, 5)
        if is_mlb:
            _mlb_text(frame, str(standing.wins)[-2:].rjust(2), 44, y, GOLD, 2)
            _mlb_text(frame, str(standing.losses)[-2:].rjust(2), 56, y, GOLD, 2)
        elif standing.points is not None:
            points = str(standing.points)[-3:]
            _tiny_text(frame, points.rjust(3), 49, y, GOLD, 3)
    return frame
