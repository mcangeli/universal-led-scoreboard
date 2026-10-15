"""Tests for optional HUB75 adapter without needing Pi GPIO or rgbmatrix."""
import sys
import types
import unittest
from unittest.mock import patch

from universal_led.display import Framebuffer
from universal_led.matrix_output import create_matrix, draw_frame


class FakeOptions:
    pass


class FakeCanvas:
    def __init__(self):
        self.pixels = {}
    def Clear(self):
        self.pixels.clear()
    def SetPixel(self, x, y, r, g, b):
        self.pixels[(x, y)] = (r, g, b)


class FakeMatrix:
    width = 64
    height = 32
    def __init__(self, options):
        self.options = options
        self.canvas = FakeCanvas()
    def CreateFrameCanvas(self):
        return self.canvas
    def SwapOnVSync(self, canvas):
        return canvas


class MatrixOutputTests(unittest.TestCase):
    def test_options_and_frame(self):
        module = types.SimpleNamespace(RGBMatrix=FakeMatrix, RGBMatrixOptions=FakeOptions)
        with patch.dict(sys.modules, {"rgbmatrix": module}):
            matrix = create_matrix()
        self.assertEqual(matrix.options.hardware_mapping, "adafruit-hat")
        self.assertEqual(matrix.options.brightness, 40)
        self.assertEqual(matrix.options.gpio_slowdown, 2)
        frame = Framebuffer()
        frame.pixel(3, 4, (1, 2, 3))
        draw_frame(matrix, frame)
        self.assertEqual(matrix.canvas.pixels[(3, 4)], (1, 2, 3))

    def test_mismatched_frame(self):
        matrix = FakeMatrix(FakeOptions())
        with self.assertRaises(ValueError):
            draw_frame(matrix, Framebuffer(32, 32))

    def test_invalid_options(self):
        with self.assertRaises(ValueError):
            create_matrix(brightness=101)


if __name__ == "__main__":
    unittest.main()
