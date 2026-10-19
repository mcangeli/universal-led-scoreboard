"""MLB standings use baseball records and durable division-specific caches."""
import tempfile
import unittest

from universal_led.football_standings_runtime import FootballStandingsCache
from universal_led.standings import Standing
from universal_led.standings_screen import render_standings, GOLD, WHITE
from universal_led.standings_rotation import StandingsRotation


class MLBStandingsDisplayTests(unittest.TestCase):
    def test_mlb_shows_wins_and_losses(self):
        row = Standing('MLB', 'NL_EAST', '144', 162, 91, 71,
                       rank=2, abbreviation='ATL')
        frame = render_standings('NL EAST', (row,))
        self.assertTrue(any(frame.pixels[y][x] == (171, 181, 170)
                            for y in range(1, 6) for x in range(17, 49)))

    def test_original_64x32_layout_has_five_rows(self):
        teams = ('ATL', 'NYM', 'PHI', 'MIA', 'WSN')
        rows = tuple(Standing('MLB', 'NL_EAST', str(i), 100,
                              70 - i, 30 + i, rank=i + 1,
                              abbreviation=team)
                     for i, team in enumerate(teams))
        frame = render_standings('NL EAST', rows)
        self.assertEqual((frame.width, frame.height), (64, 32))
        for index in range(5):
            y = 1 + index * 6
            self.assertTrue(any(frame.pixels[yy][xx] == (171, 181, 170)
                                for yy in range(y, y + 5)
                                for xx in range(1, 13)))
        for y in (0, 6, 12, 18, 24, 30):
            self.assertTrue(all(frame.pixels[y][x] == (0, 0, 255)
                                for x in range(64)))

    def test_games_back_is_visible_on_64x32(self):
        row = Standing('MLB', 'AL_EAST', '147', 100, 60, 40,
                       rank=1, abbreviation='NYY', games_back='3.5')
        with_gb = render_standings('AL EAST', (row,))
        without_gb = render_standings(
            'AL EAST', (Standing('MLB', 'AL_EAST', '147', 100, 60, 40,
                                 rank=1, abbreviation='NYY'),))
        self.assertNotEqual(with_gb.pixels, without_gb.pixels)
        self.assertTrue(any(with_gb.pixels[y][x] == (171, 181, 170)
                            for y in range(1, 6) for x in range(48, 64)))

    def test_half_game_decimal_point_is_visible(self):
        row = Standing('MLB', 'NL_EAST', '144', 100, 60, 40,
                       rank=2, abbreviation='ATL', games_back='4.5')
        frame = render_standings('NL EAST', (row,))
        # Right-aligned 4.5 starts at x=52; period occupies x=56..58.
        self.assertEqual(frame.pixels[5][57], (171, 181, 170))
        self.assertEqual(frame.pixels[4][57], (0, 0, 0))

    def test_hyphen_stays_aligned_for_three_digit_records(self):
        rows = tuple(Standing('MLB', 'AL_EAST', str(i), 160,
                              wins, 160 - wins, rank=i + 1,
                              abbreviation='NYY', games_back=str(i))
                     for i, wins in enumerate((99, 100, 101, 98, 97)))
        frame = render_standings('AL EAST', rows)
        for index in range(5):
            self.assertEqual(frame.pixels[3 + index * 6][28], (171, 181, 170))

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
