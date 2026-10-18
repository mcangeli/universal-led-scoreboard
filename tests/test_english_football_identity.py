"""Regression tests for English club identities across division changes."""
import unittest

from universal_led.english_football import Club, ClubRegistry, Membership, COMPETITIONS


class EnglishFootballIdentityTests(unittest.TestCase):
    def setUp(self):
        self.registry = ClubRegistry()
        self.wrexham = Club("espn", "12345", "Wrexham")
        self.key = self.registry.add_club(self.wrexham)

    def test_all_four_competitions(self):
        self.assertEqual(set(COMPETITIONS.values()), {"eng.1", "eng.2", "eng.3", "eng.4"})

    def test_favorite_follows_promotion(self):
        self.registry.assign(Membership(self.key, "2026-27", "CHAMPIONSHIP"))
        self.registry.assign(Membership(self.key, "2027-28", "EPL"))
        favorites = (self.key,)
        self.assertEqual(self.registry.favorites_in(favorites, "2026-27", "CHAMPIONSHIP"), favorites)
        self.assertEqual(self.registry.favorites_in(favorites, "2027-28", "EPL"), favorites)
        self.assertEqual(self.registry.favorites_in(favorites, "2027-28", "CHAMPIONSHIP"), ())
        self.assertEqual(self.key, "espn:12345")

    def test_relegation_does_not_change_club_key(self):
        self.registry.assign(Membership(self.key, "2026-27", "LEAGUE_ONE"))
        self.registry.assign(Membership(self.key, "2027-28", "LEAGUE_TWO"))
        self.assertEqual(self.registry.competition_for(self.key, "2027-28"), "LEAGUE_TWO")
        self.assertEqual(self.key, "espn:12345")

    def test_seasons_do_not_overwrite_each_other(self):
        self.registry.assign(Membership(self.key, "2026-27", "CHAMPIONSHIP"))
        self.registry.assign(Membership(self.key, "2027-28", "EPL"))
        self.assertEqual(self.registry.competition_for(self.key, "2026-27"), "CHAMPIONSHIP")

    def test_provider_qualified_keys(self):
        other = self.registry.add_club(Club("other", "12345", "Other club"))
        self.assertNotEqual(self.key, other)

    def test_unknown_club_membership_rejected(self):
        with self.assertRaises(ValueError):
            self.registry.assign(Membership("espn:missing", "2026-27", "EPL"))

    def test_unknown_competition_rejected(self):
        with self.assertRaises(ValueError):
            Membership(self.key, "2026-27", "FA_CUP")

    def test_missing_identity_rejected(self):
        with self.assertRaises(ValueError):
            Club("espn", "", "Wrexham")


if __name__ == "__main__":
    unittest.main()
