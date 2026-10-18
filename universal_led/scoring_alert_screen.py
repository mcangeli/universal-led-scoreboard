"""64x32 scoring announcement cards, independent of sport providers."""
from .display import Framebuffer
from .mlb_classic import small
from .mlb_previous_play import sanitize_play


def render_scoring_alert(event):
    """Render a confirmed scoring event with its league and scoring team."""
    frame = Framebuffer(64, 32)
    accent = (239, 195, 95)
    ink = (235, 235, 225)
    heading = sanitize_play(str(event.league).upper())[:12] or "SCORE"
    kind = sanitize_play(str(event.kind).upper())[:12] or "SCORE"
    team = sanitize_play(str(event.team_id).upper())[:12] or "TEAM"
    description = sanitize_play(str(event.description))[:15]
    small(frame, heading, 1, 1, accent)
    for x in range(64):
        frame.pixel(x, 9, (85, 100, 115))
    small(frame, kind, 1, 12, accent)
    small(frame, team, 1, 20, ink)
    if description:
        small(frame, description, 1, 27, ink)
    return frame
