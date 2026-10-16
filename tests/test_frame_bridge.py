import tempfile
import unittest
from pathlib import Path
from universal_led.display import Framebuffer
from universal_led.frame_bridge import read_frame, write_frame

class FrameBridgeTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame.ppm"
            frame = Framebuffer()
            frame.pixel(3, 4, (10, 20, 30))
            write_frame(path, frame)
            restored = read_frame(path)
            self.assertEqual(restored.pixels[4][3], (10, 20, 30))
            self.assertEqual(restored.pixels[0][0], (0, 0, 0))

    def test_rejects_invalid_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame.ppm"
            path.write_bytes(b"not a frame")
            with self.assertRaises(ValueError):
                read_frame(path)
