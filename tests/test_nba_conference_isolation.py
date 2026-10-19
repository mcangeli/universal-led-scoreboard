import tempfile
import unittest
from pathlib import Path

from universal_led.football_standings_runtime import FootballStandingsCache
from universal_led.standings import Standing
from universal_led.standings_rotation import StandingsRotation


def team(group, name, rank):
    return Standing(league='NBA', group=group, team_id=name,
                    abbreviation=name, played=10, wins=6, losses=4, rank=rank)


class NBAConferenceIsolationTests(unittest.TestCase):
    def test_separate_cache_groups_and_rotation(self):
        with tempfile.TemporaryDirectory() as folder:
            east = FootballStandingsCache(
                'NBA', fetcher=lambda _: [team('Eastern', 'ATL', 1)],
                cache_dir=folder, cache_key='nba-eastern', expected_group='Eastern')
            west = FootballStandingsCache(
                'NBA', fetcher=lambda _: [team('Western', 'DEN', 1)],
                cache_dir=folder, cache_key='nba-western', expected_group='Western')
            east.refresh()
            west.refresh()
            self.assertEqual(east.rows()[0].group, 'Eastern')
            self.assertEqual(west.rows()[0].group, 'Western')
            rotation = StandingsRotation({'Eastern': east, 'Western': west},
                                         enabled=True, selected_leagues=['Eastern', 'Western'])
            self.assertEqual(len(rotation._pages()), 2)
            self.assertEqual([page[0][1][0].group for page in rotation._pages()],
                             ['Eastern', 'Western'])
            self.assertTrue((Path(folder) / 'nba-eastern.json').exists())
            self.assertTrue((Path(folder) / 'nba-western.json').exists())

    def test_wrong_conference_does_not_replace_last_good(self):
        cache = FootballStandingsCache(
            'NBA', fetcher=lambda _: [team('Eastern', 'ATL', 1)],
            expected_group='Eastern')
        cache.refresh()
        cache.fetcher = lambda _: [team('Western', 'DEN', 1)]
        cache.refresh(force=True)
        self.assertEqual(cache.rows()[0].team_id, 'ATL')
        self.assertIsNotNone(cache.last_error)


if __name__ == '__main__':
    unittest.main()
