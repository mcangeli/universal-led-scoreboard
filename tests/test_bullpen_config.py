"""Bullpen configuration contract tests."""
import unittest
from universal_led.bullpen_config import BullpenMLBConfig, BullpenLayout, BullpenColors


class BullpenConfigTests(unittest.TestCase):
    def test_magic_number_options(self):
        config = BullpenMLBConfig({"team": "Braves", "refresh_seconds": 300})
        self.assertEqual(config.plugin_config["team"], "Braves")
        config.plugin_config["team"] = "Other"
        self.assertEqual(config.plugin_config["team"], "Braves")

    def test_layout_standings_font(self):
        font = object()
        layout = BullpenLayout(fonts={"standings.font": font})
        self.assertIs(layout.font("standings.font")["font"], font)
        self.assertEqual((layout.width, layout.height), (64, 32))

    def test_missing_font_is_explicit(self):
        with self.assertRaises(KeyError):
            BullpenLayout().font("standings.font")

    def test_color_bridge(self):
        colors = BullpenColors({"accent": (10, 20, 30)})
        self.assertEqual(colors.color("accent"), {"red": 10, "green": 20, "blue": 30})
        self.assertEqual(colors.graphics_color("accent"), (10, 20, 30))

    def test_postseason_not_guessed(self):
        with self.assertRaises(NotImplementedError):
            BullpenMLBConfig().is_postseason()


if __name__ == "__main__":
    unittest.main()
