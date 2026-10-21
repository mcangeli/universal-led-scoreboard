"""Regression checks for interleaved supplemental plugin rotation."""
import unittest
from pathlib import Path


class PluginRotationSpacingTests(unittest.TestCase):
    def test_native_plugins_are_separated_by_regular_slots(self):
        source = (Path(__file__).resolve().parents[1] / "universal_led" / "multisport_runtime.py").read_text()
        self.assertIn("durations.extend((interval, max(1, min(3600,", source)
        self.assertIn("slot_ids.extend((-1, index))", source)
        self.assertIn("plugin_index = slot_ids[index]", source)
        self.assertIn("if plugin_slots and not self._live_sports():", source)

    def test_interleaved_schedule_has_no_adjacent_plugins(self):
        durations = []
        slot_ids = []
        for index, seconds in enumerate((5, 12, 8)):
            durations.extend((10, seconds))
            slot_ids.extend((-1, index))
        self.assertEqual(slot_ids, [-1, 0, -1, 1, -1, 2])
        self.assertEqual(durations, [10, 5, 10, 12, 10, 8])


if __name__ == "__main__":
    unittest.main()
