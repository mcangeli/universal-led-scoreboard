"""Bullpen rotation gating tests."""
import unittest

from universal_led.bullpen_rotation import BullpenRotationSlot


class FakeBackground:
    def __init__(self):
        self.ticks = []
        self.frame_value = object()

    def tick(self, now=None):
        self.ticks.append(now)
        return True

    def render(self):
        return self.frame_value


class BullpenRotationTests(unittest.TestCase):
    def test_live_game_never_displays_or_ticks_plugin(self):
        worker = FakeBackground()
        slot = BullpenRotationSlot(worker)
        self.assertIsNone(slot.frame(live_games=True, selected=True, now=5))
        self.assertEqual(worker.ticks, [])

    def test_unselected_plugin_never_displays_or_ticks(self):
        worker = FakeBackground()
        slot = BullpenRotationSlot(worker)
        self.assertIsNone(slot.frame(live_games=False, selected=False, now=5))
        self.assertEqual(worker.ticks, [])

    def test_selected_nonlive_plugin_uses_cached_frame(self):
        worker = FakeBackground()
        slot = BullpenRotationSlot(worker)
        self.assertIs(slot.frame(live_games=False, selected=True, now=5), worker.frame_value)
        self.assertEqual(worker.ticks, [5])


if __name__ == "__main__":
    unittest.main()
