"""Season eligibility is checked before standings are offered to rotation."""
import unittest

from universal_led.standings import Standing
from universal_led.standings_rotation import StandingsRotation


class Cache:
    def __init__(self, rows):
        self._rows = rows

    def rows(self):
        return self._rows


def row(league, group):
    return Standing(league, group, 'ABC', 20, 10, 8, 2,
                    points=22, rank=1, abbreviation='ABC')


class SeasonAwareStandingsTests(unittest.TestCase):
    def test_offseason_cached_standings_never_enter_rotation(self):
        caches = {'Atlantic': Cache((row('NHL', 'Atlantic'),))}
        rotation = StandingsRotation(caches, enabled=True,
                                     season_policy=lambda league: False)
        self.assertFalse(rotation.has_pages())
        self.assertEqual(rotation._pages(), ())

    def test_new_season_resumes_without_changing_user_settings(self):
        active = {'Atlantic': False}
        rotation = StandingsRotation(
            {'Atlantic': Cache((row('NHL', 'Atlantic'),))},
            enabled=True, selected_leagues=['Atlantic'],
            season_policy=lambda league: active[league])
        self.assertFalse(rotation.has_pages())
        active['Atlantic'] = True
        self.assertTrue(rotation.has_pages())
        self.assertEqual(rotation.selected_leagues, frozenset({'Atlantic'}))

    def test_season_gate_is_independent_for_each_competition(self):
        caches = {
            'Atlantic': Cache((row('NHL', 'Atlantic'),)),
            'AL_EAST': Cache((row('MLB', 'AL_EAST'),)),
        }
        rotation = StandingsRotation(
            caches, enabled=True,
            season_policy=lambda league: league == 'Atlantic')
        self.assertEqual(len(rotation._pages()), 1)
        self.assertEqual(rotation._pages()[0][0][0], 'Atlantic')

    def test_disabled_user_preference_stays_disabled_during_season(self):
        rotation = StandingsRotation(
            {'Atlantic': Cache((row('NHL', 'Atlantic'),))},
            enabled=False, season_policy=lambda league: True)
        self.assertFalse(rotation.has_pages())


if __name__ == '__main__':
    unittest.main()
