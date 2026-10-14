import unittest
from universal_led.core import Canvas, Rotation
from universal_led.display import Framebuffer, splash

class FoundationTests(unittest.TestCase):
    def test_canvas_dimensions(self):
        with self.assertRaises(ValueError):
            Canvas(0, 32)
    def test_rotation_wraps(self):
        screens = [object(), object()]
        rotation = Rotation(screens)
        self.assertIs(rotation.next(), screens[0])
        self.assertIs(rotation.next(), screens[1])
        self.assertIs(rotation.next(), screens[0])
    def test_empty_rotation(self):
        with self.assertRaises(RuntimeError):
            Rotation([]).next()
    def test_splash_has_pixels_and_native_size(self):
        fb = splash()
        self.assertEqual((fb.width, fb.height), (64, 32))
        self.assertTrue(any(pixel != (0,0,0) for row in fb.pixels for pixel in row))
        self.assertTrue(fb.ppm().startswith(b'P6\n64 32\n255\n'))
    def test_out_of_bounds_clipped(self):
        fb = Framebuffer()
        fb.pixel(-1, 0, (255,255,255))
        fb.pixel(64, 0, (255,255,255))
        self.assertEqual(fb.pixels[0][0], (0,0,0))
    def test_small_splash_rejected(self):
        with self.assertRaises(ValueError):
            splash(32, 32)

if __name__ == '__main__':
    unittest.main()
