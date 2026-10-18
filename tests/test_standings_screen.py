"""64x32 standings rendering contract tests."""
import unittest

from universal_led.standings import Standing
from universal_led.standings_screen import render_standings


def row(team, rank, points):
    return Standing("EPL", "Premier League", team, 10, 5, 3, 2,
                    points=points, goal_difference=2, rank=rank)


class StandingsScreenTests(unittest.TestCase):
    def test_native_dimensions_and_visible_pixels(self):
        frame = render_standings("EPL", [row("ARS", 1, 20)])
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertTrue(any(p != (0, 0, 0) for line in frame.pixels for p in line))

    def test_empty_table_still_shows_league_heading(self):
        frame = render_standings("CHAMPIONSHIP", [])
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_pages_are_distinct(self):
        rows = [row("ARS", 1, 20), row("CHE", 2, 18),
                row("MUN", 3, 16), row("LIV", 4, 14)]
        first = render_standings("EPL", rows, offset=0)
        second = render_standings("EPL", rows, offset=3)
        self.assertNotEqual(first.pixels, second.pixels)

    def test_long_league_heading_stays_clear_of_points_header(self):
        frame = render_standings("CHAMPIONSHIP", [])
        self.assertTrue(any(pixel != (0, 0, 0) for pixel in frame.pixels[0][44:61]))
        self.assertTrue(all(frame.pixels[y][x] == (0, 0, 0)
                            for y in range(0, 7) for x in range(41, 44)))

    def test_points_are_right_aligned(self):
        short = render_standings("EPL", [row("ARS", 1, 9)])
        long = render_standings("EPL", [row("ARS", 1, 100)])
        self.assertTrue(all(short.pixels[y][x] == (0, 0, 0)
                            for y in range(10, 17) for x in range(43, 55)))
        self.assertTrue(any(long.pixels[y][x] != (0, 0, 0)
                            for y in range(10, 17) for x in range(43, 48)))

    def test_invalid_page_offset_rejected(self):
        with self.assertRaises(ValueError):
            render_standings("EPL", [], offset=-1)

    def test_untrusted_team_id_is_sanitized(self):
        frame = render_standings("EPL", [row("TEAM⚽/LONG", 1, 20)])
        self.assertEqual(frame.width, 64)


if __name__ == "__main__":
    unittest.main()
