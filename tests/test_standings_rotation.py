"""Standings adapter tests; no network access during rendering."""
import unittest

from universal_led.standings import Standing
from universal_led.standings_rotation import StandingsRotation


class Cache:
    def __init__(self, rows):
        self.value = tuple(rows)
        self.reads = 0

    def rows(self):
        self.reads += 1
        return self.value


def standing(team, rank, *, group="Premier League"):
    return Standing("EPL", group, team, 10, 5, 3, 2,
                    points=20-rank, goal_difference=rank, rank=rank)


class StandingsRotationTests(unittest.TestCase):
    def test_disabled_by_default(self):
        adapter = StandingsRotation({"EPL": Cache([standing("ARS", 1)])})
        self.assertFalse(adapter.has_pages())

    def test_enabled_renders_native_frame(self):
        adapter = StandingsRotation({"EPL": Cache([standing("ARS", 1)])},
                                    enabled=True, clock=lambda: 0)
        frame = adapter.frame()
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertTrue(any(p != (0, 0, 0) for line in frame.pixels for p in line))

    def test_three_rows_per_page(self):
        clock = [0]
        cache = Cache([standing(str(i), i) for i in range(1, 5)])
        adapter = StandingsRotation({"EPL": cache}, enabled=True,
                                    page_seconds=3, clock=lambda: clock[0])
        first = adapter.frame().pixels
        clock[0] = 3
        self.assertNotEqual(first, adapter.frame().pixels)

    def test_competitions_interleave_instead_of_exhausting_one_table(self):
        first = Cache([standing(str(i), i) for i in range(1, 8)])
        second = Cache([Standing("CHAMPIONSHIP", "Championship", str(i),
                                 10, 5, 3, 2, points=20-i,
                                 goal_difference=i, rank=i)
                        for i in range(1, 5)])
        adapter = StandingsRotation({"EPL": first, "CHAMPIONSHIP": second},
                                    enabled=True, page_seconds=3, clock=lambda: 0)
        pages = adapter._pages()
        self.assertEqual([(league, offset) for league, _, offset in pages],
                         [("EPL", 0), ("CHAMPIONSHIP", 0),
                          ("EPL", 3), ("CHAMPIONSHIP", 3),
                          ("EPL", 6)])

    def test_empty_league_does_not_block_other_tables(self):
        adapter = StandingsRotation(
            {"EPL": Cache([]), "CHAMPIONSHIP": Cache([
                Standing("CHAMPIONSHIP", "Championship", "1",
                         1, 1, 0, points=3, rank=1)])},
            enabled=True)
        self.assertEqual(len(adapter._pages()), 1)

    def test_incomplete_ranks_do_not_guess(self):
        bad = Standing("EPL", "Premier League", "ARS", 1, 1, 0,
                       points=3, goal_difference=1)
        adapter = StandingsRotation({"EPL": Cache([bad])}, enabled=True)
        self.assertFalse(adapter.has_pages())

    def test_empty_cache_is_safe(self):
        adapter = StandingsRotation({"EPL": Cache([])}, enabled=True)
        self.assertFalse(adapter.has_pages())
        self.assertEqual((adapter.frame().width, adapter.frame().height), (64, 32))

    def test_invalid_settings(self):
        with self.assertRaises(ValueError):
            StandingsRotation({}, enabled="yes")
        with self.assertRaises(ValueError):
            StandingsRotation({}, page_seconds=0)


if __name__ == "__main__":
    unittest.main()
