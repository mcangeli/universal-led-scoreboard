import unittest

from universal_led.colors import readable_on_black


class ColorContrastTests(unittest.TestCase):
    def test_dark_navy_is_brightened(self):
        result = readable_on_black((0, 0, 60))
        self.assertGreater(result[0], 0)
        self.assertGreater(result[2], result[0])

    def test_maroon_retains_red_dominance(self):
        red, green, blue = readable_on_black((80, 0, 20))
        self.assertGreater(red, blue)
        self.assertGreater(blue, green)

    def test_bright_team_color_unchanged(self):
        self.assertEqual(readable_on_black((240, 210, 90)), (240, 210, 90))

    def test_black_becomes_visible(self):
        self.assertNotEqual(readable_on_black((0, 0, 0)), (0, 0, 0))

    def test_invalid_threshold_rejected(self):
        with self.assertRaises(ValueError):
            readable_on_black((10, 20, 30), 0)


if __name__ == "__main__":
    unittest.main()
