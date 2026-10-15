"""Safe content bounds for the 64x32 matrix.

Keep a two-pixel border unlit for standalone informational screens.
"""
MARGIN=2
WIDTH=64
HEIGHT=32


def fit_small(value, available_pixels):
    """3x5 glyphs with four-pixel advance."""
    count=max(0,(available_pixels+1)//4)
    return str(value)[:count]


def small_center_x(value):
    return max(MARGIN, (WIDTH-(len(value)*4-1))//2)


def big_center_x(value):
    return max(MARGIN, (WIDTH-(len(value)*6-1))//2)
