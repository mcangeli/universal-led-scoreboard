"""Tiny, original pixel marks for MLB Classic's 64x32 live layout.

These are intentionally stylized team marks, not official MLB logo assets.
"""
from .display import FONT

# 9x7 badges, centered in the space between the abbreviation and R/H/E.
# Use distinctive team colors while retaining a compact letterform.
# Team-specific two-color monograms sized for the available 9x7 slot.
# These are original symbolic marks, not licensed MLB logos.
MARKS = {
    'AZ': ((120, 20, 46), (230, 190, 100), 'A'),
    'ARI': ((120, 20, 46), (230, 190, 100), 'A'),
    'ATL': ((18, 47, 92), (235, 45, 65), 'A'),
    'BAL': ((20, 20, 20), (245, 120, 30), 'B'),
    'BOS': ((20, 48, 90), (220, 45, 60), 'B'),
    'CHC': ((20, 55, 130), (220, 40, 55), 'C'),
    'CIN': ((185, 25, 45), (250, 250, 245), 'C'),
    'CLE': ((15, 40, 85), (225, 35, 50), 'C'),
    'COL': ((55, 30, 90), (230, 230, 235), 'C'),
    'CHW': ((25, 25, 25), (230, 230, 230), 'S'),
    'CWS': ((25, 25, 25), (230, 230, 230), 'S'),
    'DET': ((12, 40, 78), (250, 250, 250), 'D'),
    'HOU': ((12, 43, 80), (245, 115, 25), 'H'),
    'KCA': ((20, 65, 145), (240, 240, 240), 'K'),
    'KC': ((20, 65, 145), (240, 240, 240), 'K'),
    'KCR': ((20, 65, 145), (240, 240, 240), 'K'),
    'LAA': ((150, 20, 35), (235, 235, 235), 'A'),
    'LAD': ((20, 70, 170), (250, 250, 250), 'L'),
    'MIA': ((20, 25, 35), (30, 180, 205), 'M'),
    'MIL': ((20, 45, 100), (235, 185, 70), 'M'),
    'MIN': ((15, 35, 75), (230, 45, 55), 'M'),
    'NYM': ((20, 70, 145), (240, 105, 30), 'N'),
    'NYY': ((18, 35, 75), (240, 240, 240), 'N'),
    'SAC': ((15, 95, 60), (235, 190, 50), 'A'),
    'OAK': ((15, 95, 60), (235, 190, 50), 'A'),
    'ATH': ((15, 95, 60), (235, 190, 50), 'A'),
    'PHI': ((110, 20, 46), (245, 245, 245), 'P'),
    'PIT': ((25, 25, 25), (245, 195, 45), 'P'),
    'SD': ((85, 50, 25), (245, 190, 55), 'S'),
    'SDP': ((85, 50, 25), (245, 190, 55), 'S'),
    'SEA': ((15, 55, 80), (50, 195, 165), 'S'),
    'SF': ((25, 25, 25), (245, 115, 35), 'S'),
    'SFG': ((25, 25, 25), (245, 115, 35), 'S'),
    'STL': ((175, 25, 45), (245, 245, 245), 'S'),
    'TB': ((15, 45, 95), (120, 210, 210), 'T'),
    'TBR': ((15, 45, 95), (120, 210, 210), 'T'),
    'TEX': ((20, 60, 135), (230, 35, 55), 'T'),
    'TOR': ((25, 75, 155), (240, 240, 240), 'T'),
    'WSH': ((155, 25, 45), (240, 240, 240), 'W'),
}


# Transparent 11x9 pixel artwork for the live Classic screen.
# MIL is a glove-inspired open pocket around a baseball.
# LAD uses a taller interlocking L/A-inspired silhouette.
# Dots are transparent; no square badge backgrounds.
SPRITES = {
    'MIL': (
        '...GG.GG...',
        '..GGG.GGG..',
        '.GG.....GG.',
        '.G..WWW..G.',
        '.G..WWW..G.',
        '.G..WWW..G.',
        '..G.....G..',
        '..GGGGGGG..',
        '...GGGGG...',
    ),
    'LAD': (
        'B......B...',
        'B.....B.B..',
        'B....B...B.',
        'B....BBBBB.',
        'B....B...B.',
        'B....B...B.',
        'BBBB.B...B.',
        '.....B...B.',
        '.....B...B.',
    ),
}
SPRITE_COLORS = {
    'MIL': {'G': (236, 190, 69), 'W': (245, 245, 230)},
    'LAD': {'B': (40, 110, 230)},
}

def draw_team_mark(fb, team, x, y):
    """Draw a badge when artwork exists. Return False for unknown teams."""
    mark = MARKS.get(team.upper())
    if mark is None:
        return False
    sprite = SPRITES.get(team.upper())
    if sprite is not None:
        colors = SPRITE_COLORS[team.upper()]
        for dy, row in enumerate(sprite):
            for dx, symbol in enumerate(row):
                if symbol != '.':
                    fb.pixel(x + dx, y + dy, colors[symbol])
        return True
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
