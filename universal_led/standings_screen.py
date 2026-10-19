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
    "-": ("000", "000", "111", "000", "000"),
    " ": ("000",) * 5,
}


def _tiny_text(frame, value, x, y, color, limit):
    for index, char in enumerate(str(value).upper()[:limit]):
        glyph = TINY.get(char, TINY[" "])
        for dy, bits in enumerate(glyph):
            for dx, bit in enumerate(bits):
                if bit == "1":
                    frame.pixel(x + index * 4 + dx, y + dy, color)


def _render_mlb_division(frame, league, rows, offset):
    """MLB-LED-Scoreboard wide standings renderer, adapted to Framebuffer.

    Source: standings/src/mlb_led_scoreboard_standings/renderer.py
    Coordinates: coordinates/w64h32.example.json. On 64x32 the original
    games-back column starts at x=64 and is intentionally not visible.
    """
    division = league.upper().replace("_", " ")
    # Original standings.al.divider / standings.nl.divider colors.
    divider = (255, 0, 0) if division.startswith("AL") else (0, 0, 255)
    team_color = (171, 181, 170)
    stat_color = (171, 181, 170)
    # Original __render_static_wide_standings: start=0, offset=6,
    # divider x=13, name x=1, record centered at x=31.
    for x in range(64):
        frame.pixel(x, 0, divider)
    for y in range(31):
        frame.pixel(13, y, divider)
    for index, standing in enumerate(tuple(rows)[offset:offset + 5]):
        baseline = 6 + index * 6
        for x in range(64):
            frame.pixel(x, baseline, divider)
        _tiny_text(frame, standing.abbreviation or standing.team_id,
                   1, baseline - 5, team_color, 3)
        record = f"{standing.wins:>3}-{standing.losses:<3}"
        # Original center_text_position(record, x=31, font_width=4).
        record_x = 31 - (len(record) * 4) // 2
        _tiny_text(frame, record, record_x, baseline - 5, stat_color, 7)


def render_standings(league, rows, *, offset=0):
    """Display five MLB rows or three football rows without collisions."""
    if type(offset) is not int or offset < 0:
        raise ValueError("Invalid standings page offset")
    frame = Framebuffer(64, 32)
    if rows and rows[0].league == "MLB":
        _render_mlb_division(frame, league, rows, offset)
        return frame
    labels = {"CHAMPIONSHIP": "CHAMP", "LEAGUE_ONE": "LGE 1",
              "LEAGUE_TWO": "LGE 2"}
    _tiny_text(frame, labels.get(league, league), 1, 1, GOLD, 9)
    _tiny_text(frame, "PTS", 49, 1, GOLD, 3)
    for x in range(64):
        frame.pixel(x, 8, DIM)
    for index, standing in enumerate(tuple(rows)[offset:offset + 3]):
        y = 11 + index * 7
        rank = standing.rank if standing.rank is not None else offset + index + 1
        _tiny_text(frame, str(rank).rjust(2), 1, y, GREEN, 2)
        _tiny_text(frame, standing.abbreviation or standing.team_id, 15, y, WHITE, 5)
        if standing.points is not None:
            points = str(standing.points)[-3:]
            _tiny_text(frame, points.rjust(3), 49, y, GOLD, 3)
    return frame
