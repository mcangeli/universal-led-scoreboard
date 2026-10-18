"""English club directory and favorite-selector integration."""
import unittest
from universal_led.english_clubs import parse_teams
from universal_led.configurator import HTML


class EnglishClubDirectoryTests(unittest.TestCase):
    def test_espn_ids_are_stable_and_provider_qualified(self):
        payload = {"sports": [{"leagues": [{"teams": [
            {"team": {"id": "381", "displayName": "Example United"}},
            {"team": {"id": "382", "name": "Example City"}},
        ]}]}]}
        clubs = parse_teams(payload, "CHAMPIONSHIP")
        self.assertEqual([club["key"] for club in clubs], ["espn:381", "espn:382"])
        self.assertEqual(clubs[0]["division"], "CHAMPIONSHIP")

    def test_invalid_division_rejected(self):
        with self.assertRaises(ValueError):
            parse_teams({}, "MLS")

    def test_dashboard_has_search_and_saved_favorites(self):
        for fragment in ('id="english-team-search"', 'id="english-teams"',
                         "async function loadEnglishClubs(favorites)",
                         "next.english.favorite_teams=",
                         "await loadEnglishClubs(english.favorite_teams)",
                         "/api/english/clubs"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, HTML)

    def test_directory_does_not_drop_previous_favorites(self):
        self.assertIn("Previously selected", HTML)
        self.assertIn("Existing favorites will be preserved.", HTML)


if __name__ == "__main__":
    unittest.main()
