"""64x32 RGB framebuffer renderer for MLS/NWSL match and goal screens."""
from .display import FONT, Framebuffer
from .soccer_screens import SoccerScreen

WHITE = (235, 235, 235)
GOLD = (238, 189, 74)
GREEN = (90, 205, 120)


def _safe(value: str, max_chars: int = 10) -> str:
    # Framebuffer's bundled 5x7 font supports only a restricted alphabet.
    # Replace unsupported characters rather than raising on names such as O'Neil.
    normalized = "".join(char if char.upper() in FONT else " " for char in str(value).upper())
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
        text = _safe(value)
        frame.text(text, max(0, (64 - (len(text) * 6 - 1)) // 2), y, color)
    return frame
