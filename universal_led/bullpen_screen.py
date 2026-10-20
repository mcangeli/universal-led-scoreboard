"""Run an already-constructed Bullpen plugin against the ULS framebuffer.

This is a lifecycle adapter, not a plugin loader. Callers must explicitly
authorize loading third-party code and provide constructed config/data/renderer.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .bullpen_graphics import BullpenCanvas, BullpenGraphics
from .display import Framebuffer


@dataclass
class BullpenScreen:
    """Bridge Bullpen's update/can_render/render/reset lifecycle to ULS."""

    data: object
    renderer: object
    scrolling_text_pos: int = 0

    def render(self) -> Framebuffer | None:
        """Return one 64x32 frame, or None when the plugin is ineligible.

        Network throttling belongs to the plugin's data.update() method,
        consistent with Bullpen's published API. Callers must not invoke this
        on the display thread if update() may block.
        """
        status = self.data.update()
        if hasattr(status, "ok") and not status.ok():
            return None
        if not self.renderer.can_render(self.data):
            return None
        canvas = BullpenCanvas()
        position = self.renderer.render(
            self.data, canvas, BullpenGraphics, self.scrolling_text_pos
        )
        if position is not None:
            if isinstance(position, bool) or not isinstance(position, int):
                raise ValueError("Bullpen scroll position must be an integer or None")
            self.scrolling_text_pos = position
        return canvas.frame

    def wait_time(self) -> float:
        value = self.renderer.wait_time()
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Bullpen wait time must be numeric")
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Bullpen wait time must be positive and finite")
        return value

    def reset(self) -> None:
        self.scrolling_text_pos = 0
        self.renderer.reset()
