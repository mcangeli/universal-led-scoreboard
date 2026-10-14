import unittest
from unittest.mock import patch
from universal_led.backends import EmulatorBackend, Hub75Backend
from universal_led.display import Framebuffer, splash
from universal_led.web_preview import make_handler

class BackendTests(unittest.TestCase):
    def test_emulator_retains_frame(self):
        backend = EmulatorBackend()
        frame = splash()
        backend.show(frame)
        self.assertIs(backend.last_frame, frame)
        backend.close()
        self.assertIsNone(backend.last_frame)
    def test_hub75_rejects_invalid_brightness(self):
        with self.assertRaises(ValueError):
            Hub75Backend(brightness=101)
    def test_hub75_rejects_invalid_dimensions(self):
        with self.assertRaises(ValueError):
            Hub75Backend(rows=0)
    def test_web_handler_creation(self):
        handler = make_handler(splash)
        self.assertTrue(hasattr(handler, 'do_GET'))

if __name__ == '__main__':
    unittest.main()
