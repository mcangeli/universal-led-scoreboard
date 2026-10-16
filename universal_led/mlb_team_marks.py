"""Tiny, original pixel marks for MLB Classic's 64x32 live layout.

These are intentionally stylized team marks, not official MLB logo assets.
"""
from .display import FONT

# 9x7 badges, centered in the space between the abbreviation and R/H/E.
# Use distinctive team colors while retaining a compact letterform.
MARKS = {
    'ATL': ((18, 47, 92), (235, 45, 65), 'A'),
    'PHI': ((110, 20, 46), (245, 245, 245), 'P'),
}

def draw_team_mark(fb, team, x, y):
    """Draw a badge when artwork exists. Return False for unknown teams."""
    mark = MARKS.get(team.upper())
    if mark is None:
        return False
    background, foreground, letter = mark
    for dy in range(7):
        for dx in range(9):
            if dx in (0, 8) or dy in (0, 6):
                fb.pixel(x+dx, y+dy, foreground)
            else:
                fb.pixel(x+dx, y+dy, background)
    for row, bits in enumerate(FONT[letter]):
        for col, bit in enumerate(bits):
            if bit == '1':
                fb.pixel(x+2+col, y+row, foreground)
    return True
