"""Persisted football standings survive reboot and failed updates."""
import tempfile
import unittest
from universal_led.football_standings_runtime import FootballStandingsCache
from universal_led.standings import Standing


class PersistedStandingsTests(unittest.TestCase):
    def test_restart_restores_last_good_records(self):
        row = Standing("EPL", "EPL", "42", 8, 4, 2, draws=2, abbreviation="COV")
        with tempfile.TemporaryDirectory() as folder:
            first = FootballStandingsCache("EPL", fetcher=lambda league: (row,), cache_dir=folder)
            self.assertEqual(first.refresh(), (row,))
            restored = FootballStandingsCache("EPL", fetcher=lambda league: (), cache_dir=folder)
            self.assertEqual(restored.rows(), (row,))
            self.assertEqual(restored.refresh(), (row,))

    def test_corrupt_file_is_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            from pathlib import Path
            (Path(folder) / "epl.json").write_text("{broken", encoding="utf-8")
            cache = FootballStandingsCache("EPL", cache_dir=folder)
            self.assertEqual(cache.rows(), ())


if __name__ == "__main__":
    unittest.main()
