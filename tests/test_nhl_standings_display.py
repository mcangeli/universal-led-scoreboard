"""NHL 64x32 standings and consecutive division paging."""
import unittest

from universal_led.standings import Standing
from universal_led.standings_screen import render_standings, GOLD, WHITE, GREEN
from universal_led.standings_rotation import StandingsRotation


def row(i, *, group='Atlantic', overtime=2):
    return Standing('NHL', group, f'T{i}', 18 + overtime, 12, 6, overtime,
                    points=26, rank=i, abbreviation=f'T{i}')


class Cache:
    def __init__(self, rows):
        self._rows = rows

    def rows(self):
        return self._rows


class NHLStandingsDisplayTests(unittest.TestCase):
    def test_nhl_heading_and_columns_fit_matrix(self):
        frame = render_standings('Atlantic', (row(1),))
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertTrue(any(pixel == GOLD for pixel in frame.pixels[1]))
        self.assertTrue(any(pixel == WHITE for line in frame.pixels[11:16]
                            for pixel in line[:45]))
        self.assertTrue(any(pixel == GREEN for line in frame.pixels[11:16]
                            for pixel in line[49:57]))

    def test_overtime_losses_change_separate_column(self):
        first = render_standings('Atlantic', (row(1, overtime=2),))
        second = render_standings('Atlantic', (row(1, overtime=3),))
        self.assertNotEqual(first.pixels, second.pixels)
        for y in range(11, 16):
            self.assertEqual(first.pixels[y][:35], second.pixels[y][:35])
            self.assertEqual(first.pixels[y][43:], second.pixels[y][43:])

    def test_eight_team_division_uses_consecutive_sections(self):
        now = [0.0]
        rotation = StandingsRotation(
            {'NHL': Cache(tuple(row(i) for i in range(1, 9)))},
            enabled=True, page_seconds=18, clock=lambda: now[0])
        self.assertEqual([len(group) for group in rotation._pages()], [3])
        frames = []
        for second in (0, 6, 12):
            now[0] = second
            frames.append(rotation.frame().pixels)
        self.assertNotEqual(frames[0], frames[1])
        self.assertNotEqual(frames[1], frames[2])


if __name__ == '__main__':
    unittest.main()
