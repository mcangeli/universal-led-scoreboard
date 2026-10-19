"""Standings selection is independent of fetching and league enablement."""
import unittest
from universal_led.standings_rotation import StandingsRotation


class Cache:
    def __init__(self, rows):
        self._rows = rows
    def rows(self):
        return self._rows


class CompetitionSelectionTests(unittest.TestCase):
    def test_unselected_leagues_are_not_read(self):
        class Forbidden:
            def rows(self):
                raise AssertionError("Disabled competition was read")
        rotation = StandingsRotation({'EPL': Cache(()), 'CHAMPIONSHIP': Forbidden()},
                                     enabled=True, selected_leagues=['EPL'])
        self.assertFalse(rotation.has_pages())

    def test_empty_selection_disables_all_pages(self):
        rotation = StandingsRotation({'EPL': Cache(())}, enabled=True, selected_leagues=[])
        self.assertFalse(rotation.has_pages())

    def test_invalid_selection_is_rejected(self):
        rotation = StandingsRotation({'EPL': Cache(())})
        with self.assertRaises(ValueError):
            rotation.configure(selected_leagues=['UNKNOWN'])

    def test_selection_can_change_without_rebuilding_cache(self):
        rotation = StandingsRotation({'EPL': Cache(()), 'CHAMPIONSHIP': Cache(())})
        rotation.configure(selected_leagues=['EPL'])
        self.assertEqual(rotation.selected_leagues, frozenset({'EPL'}))
        rotation.configure(selected_leagues=['CHAMPIONSHIP'])
        self.assertEqual(rotation.selected_leagues, frozenset({'CHAMPIONSHIP'}))


if __name__ == '__main__':
    unittest.main()
