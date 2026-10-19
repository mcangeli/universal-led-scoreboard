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
    ".": ("000", "000", "000", "000", "010"),
    ",": ("000", "000", "000", "010", "100"),
    ":": ("000", "010", "000", "010", "000"),
    "/": ("001", "001", "010", "100", "100"),
    "+": ("000", "010", "111", "010", "000"),
    "%": ("101", "001", "010", "100", "101"),
    "'": ("010", "010", "000", "000", "000"),
    "&": ("010", "101", "010", "101", "011"),
    "(": ("001", "010", "010", "010", "001"),
    ")": ("100", "010", "010", "010", "100"),
    "?": ("110", "001", "010", "000", "010"),
    "!": ("010", "010", "010", "000", "010"),
    "#": ("101", "111", "101", "111", "101"),
    "=": ("000", "111", "000", "111", "000"),
    "*": ("101", "010", "111", "010", "101"),
    "_": ("000", "000", "000", "000", "111"),
    " ": ("000",) * 5,
}


def _tiny_text(frame, value, x, y, color, limit):
    """Draw supported glyphs; show ? rather than silently erasing unknowns."""
    for index, char in enumerate(str(value).upper()[:limit]):
        glyph = TINY.get(char, TINY["?"])
        for dy, bits in enumerate(glyph):
            for dx, bit in enumerate(bits):
                if bit == "1":
                    frame.pixel(x + index * 4 + dx, y + dy, color)


def _render_mlb_division(frame, league, rows, offset):
    """MLB-LED-Scoreboard wide standings renderer, adapted to Framebuffer.

    Source: standings/src/mlb_led_scoreboard_standings/renderer.py
    Coordinates: coordinates/w64h32.example.json. On 64x32 the original
    games-back column starts at x=64 in the original; ULS fits it at x=48.
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
        # Keep the hyphen at the same pixel in every row, including 100+ wins.
        _tiny_text(frame, str(standing.wins)[-3:].rjust(3),
                   16, baseline - 5, stat_color, 3)
        _tiny_text(frame, "-", 28, baseline - 5, stat_color, 1)
        _tiny_text(frame, str(standing.losses)[-3:].rjust(3),
                   32, baseline - 5, stat_color, 3)
        gb = standing.games_back if standing.games_back is not None else "-"
        gb = gb[-4:]
        _tiny_text(frame, gb, 64 - len(gb) * 4,
                   baseline - 5, stat_color, 4)


def _render_nhl_division(frame, league, rows, offset):
    """NHL division: team, wins, regulation losses, OTL, points.

    Three rows per 64x32 page. Overtime losses must never be merged into
    regulation losses or presented as football draws.
    """
    heading = {"Atlantic": "ATL", "Metropolitan": "MET",
               "Central": "CEN", "Pacific": "PAC"}.get(league, league[:3])
    _tiny_text(frame, heading, 0, 1, GOLD, 3)
    for label, x in (("W", 17), ("L", 27), ("O", 37), ("P", 53)):
        _tiny_text(frame, label, x, 1, GOLD, 1)
    for x in range(64):
        frame.pixel(x, 8, DIM)
    for index, standing in enumerate(tuple(rows)[offset:offset + 3]):
        y = 11 + index * 7
        _tiny_text(frame, standing.abbreviation or standing.team_id, 0, y, WHITE, 3)
        for value, x in ((standing.wins, 15), (standing.losses, 25),
                         (standing.draws, 35), (standing.points, 49)):
            _tiny_text(frame, str(value if value is not None else "-").rjust(2),
                       x, y, GREEN if x == 49 else WHITE, 2)


def _render_nba_conference(frame, league, rows, offset):
    """NBA: conference, team, wins, losses, and games behind."""
    _tiny_text(frame, 'NBA', 0, 1, GOLD, 3)
    _tiny_text(frame, 'E' if league == 'Eastern' else 'W', 13, 1, GOLD, 1)
    for label, x in (('W', 24), ('L', 36), ('GB', 48)):
        _tiny_text(frame, label, x, 1, GOLD, 2)
    for x in range(64):
        frame.pixel(x, 8, DIM)
    for index, standing in enumerate(tuple(rows)[offset:offset + 3]):
        y = 11 + index * 7
        _tiny_text(frame, standing.abbreviation or standing.team_id, 0, y, WHITE, 3)
        _tiny_text(frame, str(standing.wins)[-2:].rjust(2), 22, y, WHITE, 2)
        _tiny_text(frame, str(standing.losses)[-2:].rjust(2), 34, y, WHITE, 2)
        _tiny_text(frame, (standing.games_back or '-').strip()[:4], 48, y, GREEN, 4)


def _render_nfl_division(frame, league, rows, offset):
    """NFL 64x32 division standings: W, L and ties are separate."""
    parts = league.split()
    heading = (parts[0] + " " + parts[-1][:1]) if len(parts) == 2 else league[:5]
    _tiny_text(frame, heading, 0, 1, GOLD, 5)
    for label, x in (("W", 25), ("L", 38), ("T", 51)):
        _tiny_text(frame, label, x, 1, GOLD, 1)
    for x in range(64):
        frame.pixel(x, 8, DIM)
    for index, standing in enumerate(tuple(rows)[offset:offset + 3]):
        y = 11 + index * 7
        _tiny_text(frame, standing.abbreviation or standing.team_id, 0, y, WHITE, 3)
        for value, x in ((standing.wins, 22), (standing.losses, 35),
                         (standing.draws, 48)):
            _tiny_text(frame, str(value)[-2:].rjust(2), x, y, WHITE, 2)


def render_standings(league, rows, *, offset=0):
    """Display five MLB rows or three football rows without collisions."""
    if type(offset) is not int or offset < 0:
        raise ValueError("Invalid standings page offset")
    frame = Framebuffer(64, 32)
    if rows and rows[0].league == "MLB":
        _render_mlb_division(frame, league, rows, offset)
        return frame
    if rows and rows[0].league == "NHL":
        _render_nhl_division(frame, league, rows, offset)
        return frame
    if rows and rows[0].league == "NFL":
        _render_nfl_division(frame, league, rows, offset)
        return frame
    if rows and rows[0].league == "NBA":
        _render_nba_conference(frame, league, rows, offset)
        return frame
    labels = {"Eastern Conference": "MLS E", "Western Conference": "MLS W",
              "CHAMPIONSHIP": "CHAMP", "LEAGUE_ONE": "LGE 1",
              "LEAGUE_TWO": "LGE 2"}
    # The heading must end before the first stat column at x=23.
    _tiny_text(frame, labels.get(league, league), 1, 1, GOLD, 5)
    # Compact soccer columns: club | W | L | D | points.
    # Two-digit results fit in each stat column on the 64x32 matrix.
    for label, x in (("W", 23), ("L", 33), ("D", 43), ("P", 53)):
        _tiny_text(frame, label, x, 1, GOLD, 1)
    for x in range(64):
        frame.pixel(x, 8, DIM)
    for index, standing in enumerate(tuple(rows)[offset:offset + 3]):
        y = 11 + index * 7
        _tiny_text(frame, standing.abbreviation or standing.team_id, 0, y, WHITE, 5)
        for value, x in ((standing.wins, 22), (standing.losses, 32),
                         (standing.draws, 42)):
            _tiny_text(frame, str(value)[-2:].rjust(2), x, y, WHITE, 2)
        if standing.points is not None:
            _tiny_text(frame, str(standing.points)[-3:].rjust(3), 49, y, GOLD, 3)
    return frame
