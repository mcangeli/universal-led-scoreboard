"""Centered 64x32 scoring cards for league-neutral scoring events."""
from .display import Framebuffer
from .mlb_classic import small
from .mlb_previous_play import sanitize_play


def _center(frame, text, y, color):
    text = sanitize_play(str(text).upper())[:15]
    if text:
        small(frame, text, max(0, (64 - 4 * len(text)) // 2), y, color)


def render_scoring_alert(event):
    """Show league, scoring event, matchup score and optional credited player."""
    frame = Framebuffer(64, 32)
    accent = (239, 195, 95)
    ink = (235, 235, 225)
    _center(frame, str(event.league)[:15] or "SCORE", 1, accent)
    for x in range(64):
        frame.pixel(x, 9, (85, 100, 115))
    _center(frame, str(event.kind)[:15] or "SCORE", 11, accent)
    home = getattr(event, "home_team", "")
    away = getattr(event, "away_team", "")
    hs = getattr(event, "home_score", None)
    aws = getattr(event, "away_score", None)
    if home and away and type(hs) is int and type(aws) is int:
        # Shorten codes if necessary without losing the score.
        score = f"{str(away)[:3].upper()} {aws}-{hs} {str(home)[:3].upper()}"
        _center(frame, score, 19, ink)
    else:
        _center(frame, event.team_id, 19, ink)
    if event.description:
        _center(frame, event.description, 27, ink)
    return frame
