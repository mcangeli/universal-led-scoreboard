"""Optional physical HUB75 output using hzeller/rpi-rgb-led-matrix Python bindings.

The import is intentionally deferred so emulator-only installations remain usable.
"""
from __future__ import annotations

from .display import Framebuffer


def create_matrix(*, rows=32, cols=64, chain_length=1, parallel=1,
                  gpio_mapping="adafruit-hat", brightness=40, gpio_slowdown=2):
    if rows <= 0 or cols <= 0 or chain_length <= 0 or parallel <= 0:
        raise ValueError("Matrix dimensions and chain counts must be positive")
    if not 1 <= brightness <= 100 or gpio_slowdown < 0:
        raise ValueError("Invalid brightness or GPIO slowdown")
    try:
        from rgbmatrix import RGBMatrix, RGBMatrixOptions
    except ImportError as exc:
        raise RuntimeError(
            "rgbmatrix Python bindings are missing. Install the rpi-rgb-led-matrix "
            "Python bindings before enabling physical output."
        ) from exc
    options = RGBMatrixOptions()
    options.rows = rows
    options.cols = cols
    options.chain_length = chain_length
    options.parallel = parallel
    options.hardware_mapping = gpio_mapping
    options.brightness = brightness
    options.gpio_slowdown = gpio_slowdown
    return RGBMatrix(options=options)


def draw_frame(matrix, frame: Framebuffer, *, canvas=None):
    """Draw a complete framebuffer using the driver's double buffer."""
    if frame.width != matrix.width or frame.height != matrix.height:
        raise ValueError(
            f"Framebuffer {frame.width}x{frame.height} does not match "
            f"matrix {matrix.width}x{matrix.height}"
        )
    if canvas is None:\n        canvas = matrix.CreateFrameCanvas()
    canvas.Clear()
    for y, row in enumerate(frame.pixels):
        for x, (red, green, blue) in enumerate(row):
            canvas.SetPixel(x, y, red, green, blue)
    return matrix.SwapOnVSync(canvas)
