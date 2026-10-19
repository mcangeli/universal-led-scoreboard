"""Season status provider contract and cached phase behavior."""
import unittest

from universal_led.standings_season_status import StandingsSeasonStatus


class StandingsSeasonStatusTests(unittest.TestCase):
    def test_unknown_does_not_claim_offseason_or_display_stale_table(self):
        status = StandingsSeasonStatus()
        self.assertEqual(status.phase('Atlantic'), 'unknown')
        self.assertFalse(status.eligible('Atlantic'))

    def test_regular_season_is_eligible(self):
        status = StandingsSeasonStatus()
        status.update('Atlantic', 'regular')
        self.assertTrue(status.eligible('Atlantic'))

    def test_postseason_requires_a_supported_postseason_display(self):
        status = StandingsSeasonStatus()
        status.update('Atlantic', 'postseason')
        self.assertFalse(status.eligible('Atlantic'))
        self.assertTrue(status.eligible('Atlantic', postseason_supported=True))

    def test_offseason_is_ineligible(self):
        status = StandingsSeasonStatus()
        status.update('Atlantic', 'offseason')
        self.assertFalse(status.eligible('Atlantic'))

    def test_failed_refresh_keeps_last_confirmed_phase(self):
        status = StandingsSeasonStatus()
        status.update('Atlantic', 'regular')
        self.assertEqual(status.failed('Atlantic'), 'regular')
        self.assertTrue(status.eligible('Atlantic'))

    def test_competitions_are_independent(self):
        status = StandingsSeasonStatus()
        status.update('Atlantic', 'offseason')
        status.update('EPL', 'regular')
        self.assertFalse(status.eligible('Atlantic'))
        self.assertTrue(status.eligible('EPL'))

    def test_invalid_phase_rejected_without_mutation(self):
        status = StandingsSeasonStatus()
        status.update('Atlantic', 'regular')
        with self.assertRaises(ValueError):
            status.update('Atlantic', 'playoffs-ish')
        self.assertEqual(status.phase('Atlantic'), 'regular')


if __name__ == '__main__':
    unittest.main()
