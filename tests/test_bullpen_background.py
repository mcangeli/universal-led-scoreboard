"""Deterministic background Bullpen rendering tests."""
import threading
import time
import unittest

from universal_led.bullpen_background import BullpenBackgroundScreen
from universal_led.bullpen_screen import BullpenScreen


class Data:
    def __init__(self):
        self.started = threading.Event()
        self.release = threading.Event()
        self.calls = 0

    def update(self):
        self.calls += 1
        self.started.set()
        self.release.wait(2)
        return None


class Renderer:
    def can_render(self, data):
        return True

    def render(self, data, canvas, graphics, position):
        canvas.SetPixel(0, 0, 40, 50, 60)

    def wait_time(self):
        return 0.1

    def reset(self):
        pass


class BullpenBackgroundTests(unittest.TestCase):
    def test_render_returns_immediately_during_network_update(self):
        data = Data()
        background = BullpenBackgroundScreen(BullpenScreen(data, Renderer()))
        try:
            self.assertTrue(background.refresh())
            self.assertTrue(data.started.wait(1))
            start = time.monotonic()
            self.assertIsNone(background.render())
            self.assertLess(time.monotonic() - start, 0.2)
            self.assertFalse(background.refresh())
            data.release.set()
            deadline = time.monotonic() + 2
            while background.render() is None and time.monotonic() < deadline:
                time.sleep(0.005)
            self.assertEqual(background.render().pixels[0][0], (40, 50, 60))
            self.assertEqual(data.calls, 1)
        finally:
            data.release.set()
            background.close()

    def test_redraw_advances_scroll_without_network_call(self):
        class ScrollingRenderer(Renderer):
            def render(self, data, canvas, graphics, position):
                canvas.SetPixel(position, 0, 40, 50, 60)
                return None
        data = Data()
        background = BullpenBackgroundScreen(BullpenScreen(data, ScrollingRenderer()))
        try:
            self.assertTrue(background.refresh())
            self.assertTrue(data.started.wait(1))
            data.release.set()
            deadline = time.monotonic() + 2
            while background.render() is None and time.monotonic() < deadline:
                time.sleep(0.005)
            self.assertIsNotNone(background.render())
            self.assertTrue(background.advance_frame())
            deadline = time.monotonic() + 2
            while background.render().pixels[0][1] != (40, 50, 60) and time.monotonic() < deadline:
                time.sleep(0.005)
            self.assertEqual(background.render().pixels[0][1], (40, 50, 60))
            self.assertEqual(data.calls, 1)
        finally:
            data.release.set()
            background.close()

    def test_closed_background_rejects_refresh(self):
        background = BullpenBackgroundScreen(BullpenScreen(Data(), Renderer()))
        background.close()
        self.assertFalse(background.refresh())
        self.assertIsNone(background.render())


if __name__ == "__main__":
    unittest.main()
