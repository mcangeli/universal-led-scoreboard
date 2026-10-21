"""Subset of Bullpen's RGBMatrix graphics API backed by ULS Framebuffer.

Pure Python, hardware-independent. Does not import or execute a plugin.
"""
from __future__ import annotations

from .display import Framebuffer


class BullpenCanvas:
    def __init__(self, frame: Framebuffer | None = None):
        self.frame = frame if frame is not None else Framebuffer(64, 32)
        self.width = self.frame.width
        self.height = self.frame.height

    def SetPixel(self, x, y, r, g, b):
        self.frame.pixel(int(x), int(y), _rgb((r, g, b)))

    def Clear(self):
        self.frame = Framebuffer(self.width, self.height)

    def Fill(self, r, g, b):
        color = _rgb((r, g, b))
        for y in range(self.height):
            for x in range(self.width):
                self.frame.pixel(x, y, color)


class BullpenGraphics:
    @staticmethod
    def Color(r=0, g=0, b=0):
        return _rgb((r, g, b))

    @staticmethod
    def DrawLine(canvas, x1, y1, x2, y2, color):
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
        dx, dy = abs(x2-x1), abs(y2-y1)
        sx, sy = (1 if x1 < x2 else -1), (1 if y1 < y2 else -1)
        error = dx-dy
        while True:
            canvas.frame.pixel(x1, y1, _rgb(color))
            if x1 == x2 and y1 == y2:
                break
            twice = 2*error
            if twice > -dy:
                error -= dy
                x1 += sx
            if twice < dx:
                error += dx
                y1 += sy

    @staticmethod
    def DrawCircle(canvas, x, y, radius, color):
        radius = int(radius)
        if radius < 0:
            raise ValueError("radius must be nonnegative")
        x, y = int(x), int(y)
        px, py, error = radius, 0, 1-radius
        while px >= py:
            for dx, dy in ((px,py),(py,px),(-py,px),(-px,py),
                           (-px,-py),(-py,-px),(py,-px),(px,-py)):
                canvas.frame.pixel(x+dx, y+dy, _rgb(color))
            py += 1
            if error < 0:
                error += 2*py+1
            else:
                px -= 1
                error += 2*(py-px)+1

    @staticmethod
    def DrawText(canvas, font, x, y, color, text):
        """Draw with baseline semantics; return glyph advance width, not endpoint.

        This is a fallback for simple ASCII plugins, not a replacement for
        Bullpen's BDF font loader or full graphics API.
        """
        x, y = int(x), int(y)
        height = int(getattr(font, "height", 7))
        if height < 1:
            raise ValueError("invalid font height")
        label = str(text)
        canvas.frame.text(label, x, y-height+1, _rgb(color))
        return len(label)*6


def _rgb(color):
    if isinstance(color, tuple) and len(color) == 3:
        values = color
    elif all(hasattr(color, part) for part in ("red", "green", "blue")):
        values = (color.red, color.green, color.blue)
    else:
        raise ValueError("expected RGB color")
    if any(not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 255 for value in values):
        raise ValueError("RGB channels must be integers from 0 to 255")
    return tuple(values)
