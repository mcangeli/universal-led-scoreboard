"""Regression checks for compact standings column labels and league routing."""
import inspect
import unittest

from universal_led import standings_rotation, standings_screen
from universal_led.standings import Standing


class StandingsLayoutTests(unittest.TestCase):
    def test_nfl_rotation_passes_division_name(self):
        source = inspect.getsource(standings_rotation.StandingsRotation.frame_for_slot)
        self.assertIn("('NHL', 'NBA', 'NFL', 'MLS')", source)

    def test_mls_conference_headings_are_present(self):
        source = inspect.getsource(standings_screen.render_standings)
        self.assertIn('"Eastern Conference": "MLS EAST"', source)
        self.assertIn('"Western Conference": "MLS WEST"', source)

    def test_soccer_layout_contains_all_four_stat_columns(self):
        source = inspect.getsource(standings_screen.render_standings)
        for label in ('("W", 23)', '("L", 33)', '("D", 43)', '("P", 53)'):
            self.assertIn(label, source)

    def test_soccer_render_accepts_draws_and_points(self):
        row = Standing(league="EPL", group="EPL", team_id="ARS",
                       abbreviation="ARS", played=6, wins=3, losses=1,
                       draws=2, points=11, rank=1)
        frame = standings_screen.render_standings("EPL", [row])
        self.assertIsNotNone(frame)

    def test_nfl_render_accepts_ties(self):
        row = Standing(league="NFL", group="AFC East", team_id="BUF",
                       abbreviation="BUF", played=6, wins=4, losses=1,
                       draws=1, rank=1)
        self.assertIsNotNone(standings_screen.render_standings("AFC East", [row]))


if __name__ == "__main__":
    unittest.main()
