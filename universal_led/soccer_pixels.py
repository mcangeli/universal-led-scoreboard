"""64x32 RGB framebuffer renderer for all supported soccer leagues."""
from .display import FONT, Framebuffer

SOCCER_GLYPHS = {
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
}
from .soccer_screens import SoccerScreen

WHITE = (235, 235, 235)
GOLD = (238, 189, 74)
GREEN = (90, 205, 120)



# Compact 3x5 figures fit full W-D-L records beside club abbreviations.
RECORD_FONT = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
    "-": ("000", "000", "111", "000", "000"),
}


def _pregame_team_line(frame, value, y, color):
    """Draw club in 5x7 and full record in compact 3x5."""
    club, separator, record = value.rpartition(" ")
    if not separator or not record or not all(ch in RECORD_FONT for ch in record):
        return False
    record_width = 4 * len(record) - 1
    club = _safe(club, 5)
    side_padding = 2
    gap = 2
    max_club = max(1, (64 - 2 * side_padding - record_width - gap + 1) // 6)
    club = club[:max_club]
    frame.text(club, side_padding, y, color)
    start = 64 - side_padding - record_width
    for index, char in enumerate(record):
        for dy, bits in enumerate(RECORD_FONT[char]):
            for dx, bit in enumerate(bits):
                if bit == "1":
                    frame.pixel(start + index * 4 + dx, y + 1 + dy, color)
    return True

def _safe(value: str, max_chars: int = 10) -> str:
    # Framebuffer's bundled 5x7 font supports only a restricted alphabet.
    # Replace unsupported characters rather than raising on names such as O'Neil.
    normalized = "".join(char if char.upper() in FONT or char in SOCCER_GLYPHS else " " for char in str(value).upper())
    return " ".join(normalized.split())[:max_chars]


def render_soccer_screen(screen: SoccerScreen) -> Framebuffer:
    """Render a prepared soccer screen using the existing 64x32 framebuffer."""
    frame = Framebuffer()
    if screen.kind == "goal":
        rows = (
            (screen.header, 0, GOLD),
            (screen.line1, 8, WHITE),
            (screen.line2, 16, GREEN),
            (screen.footer, 24, GOLD),
        )
    else:
        rows = (
            (screen.header, 0, GOLD),
            (screen.line1, 8, WHITE),
            (screen.line2, 16, GREEN),
            (screen.footer, 24, GOLD),
        )
    for value, y, color in rows:
        if screen.kind == "match" and y in (8, 16) and _pregame_team_line(frame, value, y, color):
            continue
        text = _safe(value)
        x0 = max(0, (64 - (len(text) * 6 - 1)) // 2)
        for index, char in enumerate(text):
            if char in SOCCER_GLYPHS:
                for row, bits in enumerate(SOCCER_GLYPHS[char]):
                    for col, bit in enumerate(bits):
                        if bit == "1":
                            frame.pixel(x0 + index * 6 + col, y + row, color)
            else:
                frame.text(char, x0 + index * 6, y, color)
    return frame
