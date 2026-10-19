"""MLB standings use baseball records and durable division-specific caches."""
import tempfile
import unittest

from universal_led.football_standings_runtime import FootballStandingsCache
from universal_led.standings import Standing
from universal_led.standings_screen import render_standings, GOLD, WHITE
from universal_led.standings_rotation import StandingsRotation


class MLBStandingsDisplayTests(unittest.TestCase):
    def test_mlb_shows_wins_and_losses(self):
        row = Standing('MLB', 'NL_EAST', '144', 162, 91, 71, rank=2, abbreviation='ATL')
        frame = render_standings('NL EAST', (row,))
        self.assertTrue(any(frame.pixels[y][x] == GOLD
                            for y in range(7, 12) for x in range(44, 52)))
        self.assertTrue(any(frame.pixels[y][x] == GOLD
                            for y in range(7, 12) for x in range(56, 64)))

    def test_all_five_teams_fit_one_page(self):
        teams = ('ATL', 'NYM', 'PHI', 'MIA', 'WSN')
        rows = tuple(Standing('MLB', 'NL_EAST', str(i), 100,
                              70 - i, 30 + i, rank=i + 1, abbreviation=team)
                     for i, team in enumerate(teams))
        frame = render_standings('NL EAST', rows)
        self.assertEqual((frame.width, frame.height), (64, 32))
        for index in range(5):
            y = 7 + index * 5
            self.assertTrue(any(frame.pixels[yy][xx] == WHITE
                                for yy in range(y, y + 5)
                                for xx in range(11, 23)))
        self.assertTrue(all(frame.pixels[6][x] != WHITE for x in range(64)))
        for y in (11, 16, 21, 26, 31):
            self.assertTrue(all(frame.pixels[y][x] == (0, 0, 0)
                                for x in range(64)), f'Row {y} must separate teams')

    def test_mlb_division_is_single_rotation_page(self):
        rows = tuple(Standing('MLB', 'NL_EAST', str(i), 100,
                              70 - i, 30 + i, rank=i + 1, abbreviation='ATL')
                     for i in range(5))
        class Cache:
            def rows(self):
                return rows
        rotation = StandingsRotation({'NL_EAST': Cache()}, enabled=True)
        self.assertEqual(len(rotation._pages()), 1)

    def test_division_caches_do_not_collide(self):
        row = Standing('MLB', 'NL_EAST', '144', 162, 91, 71, rank=2, abbreviation='ATL')
        with tempfile.TemporaryDirectory() as directory:
            east = FootballStandingsCache('MLB', cache_dir=directory,
                                          cache_key='mlb-nl_east', fetcher=lambda _: (row,))
            east.refresh(force=True)
            west = FootballStandingsCache('MLB', cache_dir=directory,
                                          cache_key='mlb-nl_west', fetcher=lambda _: ())
            self.assertEqual(east.rows(), (row,))
            self.assertEqual(west.rows(), ())
            restored = FootballStandingsCache('MLB', cache_dir=directory,
                                              cache_key='mlb-nl_east', fetcher=lambda _: ())
            self.assertEqual(restored.rows(), (row,))


if __name__ == '__main__':
    unittest.main()
