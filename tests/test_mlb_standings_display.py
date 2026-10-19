"""MLB standings use baseball records and durable division-specific caches."""
import tempfile
import unittest

from universal_led.football_standings_runtime import FootballStandingsCache
from universal_led.standings import Standing
from universal_led.standings_screen import render_standings, GOLD


class MLBStandingsDisplayTests(unittest.TestCase):
    def test_mlb_shows_wins_and_losses(self):
        row = Standing('MLB', 'NL_EAST', '144', 162, 91, 71, rank=2, abbreviation='ATL')
        frame = render_standings('NL EAST', (row,))
        self.assertTrue(any(frame.pixels[y][x] == GOLD
                            for y in range(11, 16) for x in range(44, 52)))
        self.assertTrue(any(frame.pixels[y][x] == GOLD
                            for y in range(11, 16) for x in range(56, 64)))

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
