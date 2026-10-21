"""Regression fixtures for real Bullpen plugin package metadata.

These entry points are from mcangeli/mlb-magic-number (0.3.1) and
mcangeli/MLB-LED-BGS (1.5.4). No external code is installed or imported.
"""
import tempfile
import unittest
from pathlib import Path

from universal_led.bullpen_compat import detect_bullpen_package


class ExistingBullpenMetadataTests(unittest.TestCase):
    def test_magic_number_entry_point(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "pyproject.toml").write_text(
                '[project]\nname = "mlb-led-scoreboard-magic-number"\n'
                'version = "0.3.1"\n'
                '[project.entry-points."bullpen.mlbled.plugin"]\n'
                '"magic_number" = "mlb_led_scoreboard_magic_number:load"\n'
            )
            found = detect_bullpen_package(directory)
            self.assertEqual([(x.name, x.entry_point) for x in found],
                             [("magic_number", "mlb_led_scoreboard_magic_number:load")])

    def test_green_monster_entry_point(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "pyproject.toml").write_text(
                '[project]\nname = "mlb-led-scoreboard-green-monster"\n'
                'version = "1.5.4"\n'
                "[project.entry-points.'bullpen.mlbled.plugin']\n"
                '"green_monster" = "mlb_led_scoreboard_green_monster:load"\n'
            )
            found = detect_bullpen_package(directory)
            self.assertEqual([(x.name, x.entry_point) for x in found],
                             [("green_monster", "mlb_led_scoreboard_green_monster:load")])


if __name__ == "__main__":
    unittest.main()
