"""Lifecycle tests with a representative Bullpen-style plugin."""
import unittest

from universal_led.bullpen_screen import BullpenScreen


class FakeStatus:
    def __init__(self, good=True):
        self.good = good

    def ok(self):
        return self.good


class FakeData:
    def __init__(self):
        self.calls = 0
        self.status = FakeStatus()

    def update(self, force=False):
        self.calls += 1
        return self.status


class FakeRenderer:
    def __init__(self):
        self.allowed = True
        self.positions = []
        self.resets = 0

    def can_render(self, data):
        return self.allowed

    def render(self, data, canvas, graphics, position):
        self.positions.append(position)
        graphics.DrawLine(canvas, 0, 0, 2, 0, graphics.Color(0, 200, 0))
        return position + 1

    def wait_time(self):
        return 0.5

    def reset(self):
        self.resets += 1


class BullpenScreenTests(unittest.TestCase):
    def test_renders_frame_and_advances_scroll(self):
        data, renderer = FakeData(), FakeRenderer()
        screen = BullpenScreen(data, renderer)
        frame = screen.render()
        self.assertEqual(frame.pixels[0][0], (0, 200, 0))
        self.assertEqual((data.calls, renderer.positions), (1, [0]))
        screen.render()
        self.assertEqual(renderer.positions, [0, 1])

    def test_none_return_advances_standard_bullpen_marquee(self):
        class StandardRenderer(FakeRenderer):
            def render(self, data, canvas, graphics, position):
                self.positions.append(position)
                return None
        renderer = StandardRenderer()
        screen = BullpenScreen(FakeData(), renderer)
        screen.render()
        screen.render()
        self.assertEqual(renderer.positions, [0, 1])
        self.assertEqual(screen.scrolling_text_pos, 2)

    def test_skips_when_ineligible(self):
        data, renderer = FakeData(), FakeRenderer()
        renderer.allowed = False
        screen = BullpenScreen(data, renderer)
        self.assertIsNone(screen.render())
        self.assertEqual(renderer.positions, [])

    def test_skips_failed_data_update(self):
        data, renderer = FakeData(), FakeRenderer()
        data.status = FakeStatus(False)
        self.assertIsNone(BullpenScreen(data, renderer).render())
        self.assertEqual(renderer.positions, [])

    def test_reset_and_wait_time(self):
        data, renderer = FakeData(), FakeRenderer()
        screen = BullpenScreen(data, renderer)
        screen.render()
        self.assertEqual(screen.wait_time(), 0.5)
        screen.reset()
        self.assertEqual(screen.scrolling_text_pos, 0)
        self.assertEqual(renderer.resets, 1)

    def test_invalid_wait_time_rejected(self):
        class Broken(FakeRenderer):
            def wait_time(self):
                return float("nan")
        with self.assertRaises(ValueError):
            BullpenScreen(FakeData(), Broken()).wait_time()


if __name__ == "__main__":
    unittest.main()
