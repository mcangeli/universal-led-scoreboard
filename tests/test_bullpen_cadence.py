"""Bullpen redraw cadence tests."""
import unittest

from universal_led.bullpen_cadence import BullpenCadence


class BullpenCadenceTests(unittest.TestCase):
    def test_magic_number_frame_interval(self):
        cadence = BullpenCadence(0.12, start=10.0)
        self.assertFalse(cadence.due(10.119))
        self.assertTrue(cadence.due(10.12))
        cadence.advance(10.12)
        self.assertFalse(cadence.due(10.2))
        self.assertTrue(cadence.due(10.24))

    def test_missed_ticks_do_not_burst(self):
        cadence = BullpenCadence(0.12, start=0.0)
        cadence.advance(10.0)
        self.assertFalse(cadence.due(10.0))
        self.assertTrue(cadence.due(10.12))

    def test_reset(self):
        cadence = BullpenCadence(0.5, start=0)
        cadence.reset(4)
        self.assertFalse(cadence.due(4.4))
        self.assertTrue(cadence.due(4.5))

    def test_invalid_interval(self):
        for value in (0, -1, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                BullpenCadence(value)


if __name__ == "__main__":
    unittest.main()
