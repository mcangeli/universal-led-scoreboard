"""Tests for ESPN club discovery and season-specific memberships."""
import unittest
from datetime import date

from universal_led.english_discovery import discover_clubs, register_discovered, season_for
from universal_led.english_football import ClubRegistry


def fixture(team_id="381", name="Wrexham"):
    return {"events": [{"id": "fixture1", "competitions": [{"competitors": [
        {"homeAway": "home", "team": {"id": team_id, "displayName": name, "abbreviation": "WRX"}},
        {"homeAway": "away", "team": {"id": "42", "displayName": "Other FC"}}]}]}]}


class EnglishDiscoveryTests(unittest.TestCase):
    def test_season_boundary(self):
        self.assertEqual(season_for(date(2026, 6, 30)), "2025-26")
        self.assertEqual(season_for(date(2026, 7, 1)), "2026-27")

    def test_uses_espn_ids_not_abbreviations(self):
        pairs = discover_clubs(fixture(), "CHAMPIONSHIP", "2026-27")
        self.assertEqual(pairs[0][0].key, "espn:381")
        self.assertEqual(pairs[0][1].competition, "CHAMPIONSHIP")

    def test_club_promotion_keeps_favorite(self):
        registry = ClubRegistry()
        register_discovered(registry, fixture(), "CHAMPIONSHIP", "2026-27")
        register_discovered(registry, fixture(name="Wrexham AFC"), "EPL", "2027-28")
        self.assertEqual(registry.competition_for("espn:381", "2026-27"), "CHAMPIONSHIP")
        self.assertEqual(registry.competition_for("espn:381", "2027-28"), "EPL")
        self.assertEqual(registry.favorites_in(("espn:381",), "2027-28", "EPL"), ("espn:381",))

    def test_empty_day_does_not_erase_membership(self):
        registry = ClubRegistry()
        register_discovered(registry, fixture(), "CHAMPIONSHIP", "2026-27")
        self.assertEqual(register_discovered(registry, {"events": []}, "CHAMPIONSHIP", "2026-27"), 0)
        self.assertEqual(registry.competition_for("espn:381", "2026-27"), "CHAMPIONSHIP")

    def test_deduplicates_clubs(self):
        payload = fixture()
        payload["events"].append(payload["events"][0])
        self.assertEqual(len(discover_clubs(payload, "CHAMPIONSHIP", "2026-27")), 2)

    def test_missing_id_does_not_invent_identity(self):
        pairs = discover_clubs(fixture(team_id=""), "CHAMPIONSHIP", "2026-27")
        self.assertEqual(len(pairs), 1)

    def test_invalid_payload_rejected(self):
        with self.assertRaises(ValueError):
            discover_clubs({}, "EPL", "2026-27")

    def test_invalid_competition_rejected(self):
        with self.assertRaises(ValueError):
            discover_clubs(fixture(), "CUP", "2026-27")


if __name__ == "__main__":
    unittest.main()
