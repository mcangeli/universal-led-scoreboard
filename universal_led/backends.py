"""Display output backends. Native hardware is always opt-in."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from .display import Framebuffer

class DisplayBackend(Protocol):
    def show(self, frame: Framebuffer) -> None: ...
    def close(self) -> None: ...

@dataclass
class EmulatorBackend:
    """Retain the most recent frame for web preview and tests."""
    last_frame: Framebuffer | None = None
    def show(self, frame: Framebuffer) -> None:
        self.last_frame = frame
    def close(self) -> None:
        self.last_frame = None

class Hub75Backend:
    """Optional hzeller RGB matrix adapter; no native import in emulator mode."""
    def __init__(self, rows: int = 32, cols: int = 64, chain_length: int = 1,
                 parallel: int = 1, brightness: int = 60,
                 hardware_mapping: str = 'regular'):
        if min(rows, cols, chain_length, parallel) < 1:
            raise ValueError('Matrix dimensions and chain counts must be positive')
        if not 1 <= brightness <= 100:
            raise ValueError('Brightness must be between 1 and 100')
        try:
            from rgbmatrix import RGBMatrix, RGBMatrixOptions
        except ImportError as exc:
            raise RuntimeError('HUB75 backend requires the optional rgbmatrix Python bindings') from exc
        options = RGBMatrixOptions()
        options.rows = rows
        options.cols = cols
        options.chain_length = chain_length
        options.parallel = parallel
        options.brightness = brightness
        options.hardware_mapping = hardware_mapping
        self.matrix = RGBMatrix(options=options)
        self.width = rows * 0 + cols * chain_length
        self.height = rows * parallel
        self._canvas = self.matrix.CreateFrameCanvas()
    def show(self, frame: Framebuffer) -> None:
        if (frame.width, frame.height) != (self.width, self.height):
            raise ValueError(f'Frame size must be {self.width}x{self.height}')
        self._canvas.Clear()
        for y, row in enumerate(frame.pixels):
            for x, (r, g, b) in enumerate(row):
                self._canvas.SetPixel(x, y, r, g, b)
        self._canvas = self.matrix.SwapOnVSync(self._canvas)
    def close(self) -> None:
        self._canvas.Clear()
        self.matrix.Clear()
