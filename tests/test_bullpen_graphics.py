"""Tests for the ULS framebuffer-backed Bullpen graphics subset."""
import unittest
from universal_led.bullpen_graphics import BullpenCanvas, BullpenGraphics


class BullpenGraphicsTests(unittest.TestCase):
    def test_pixel_and_fill(self):
        canvas = BullpenCanvas()
        canvas.SetPixel(1, 2, 12, 34, 56)
        self.assertEqual(canvas.frame.pixels[2][1], (12, 34, 56))
        canvas.Fill(3, 4, 5)
        self.assertEqual(canvas.frame.pixels[2][1], (3, 4, 5))
        canvas.Clear()
        self.assertEqual(canvas.frame.pixels[2][1], (0, 0, 0))

    def test_line(self):
        canvas = BullpenCanvas()
        BullpenGraphics.DrawLine(canvas, 0, 0, 3, 0, (255, 0, 0))
        self.assertEqual([canvas.frame.pixels[0][i] for i in range(4)], [(255, 0, 0)] * 4)

    def test_circle(self):
        canvas = BullpenCanvas()
        BullpenGraphics.DrawCircle(canvas, 10, 10, 3, (0, 255, 0))
        self.assertEqual(canvas.frame.pixels[10][13], (0, 255, 0))
        self.assertEqual(canvas.frame.pixels[10][7], (0, 255, 0))

    def test_text_baseline(self):
        canvas = BullpenCanvas()
        end = BullpenGraphics.DrawText(canvas, None, 1, 7, (255, 255, 255), "A")
        self.assertEqual(end, 6)
        self.assertIn((255, 255, 255), canvas.frame.pixels[1])

    def test_text_width_independent_of_draw_origin(self):
        canvas = BullpenCanvas()
        self.assertEqual(BullpenGraphics.DrawText(canvas, None, -1000, 0, (0, 0, 0), "ATL"), 18)
        self.assertEqual(BullpenGraphics.DrawText(canvas, None, 3, 7, (255, 255, 255), "ATL"), 18)

    def test_invalid_color(self):
        with self.assertRaises(ValueError):
            BullpenGraphics.Color(256, 0, 0)


if __name__ == "__main__":
    unittest.main()
