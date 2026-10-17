import unittest
from datetime import date

from universal_led.soccer import SoccerMatch
from universal_led.soccer_native import parse_mls_matches, parse_nwsl_matches
from universal_led.soccer_providers import SoccerProviderRouter, ProviderUnavailable


def match(league="MLS"):
    return SoccerMatch("1", league, "ATL", "MIA", 1, 0, "live")


class SoccerProviderTests(unittest.TestCase):
    def test_primary_preferred(self):
        router = SoccerProviderRouter("MLS", primary=lambda d: [match()],
                                      fallback=lambda d: self.fail("fallback called"))
        self.assertEqual(router.fetch(date.today()), (match(),))
        self.assertEqual(router.last_source, "league")

    def test_fallback_after_primary_failure(self):
        router = SoccerProviderRouter("MLS", primary=lambda d: (_ for _ in ()).throw(OSError("offline")),
                                      fallback=lambda d: [match()])
        self.assertEqual(router.fetch(date.today()), (match(),))
        self.assertEqual(router.last_source, "espn")
        self.assertIn("offline", router.last_primary_error)

    def test_empty_primary_does_not_trigger_fallback(self):
        router = SoccerProviderRouter("MLS", primary=lambda d: [],
                                      fallback=lambda d: self.fail("fallback called"))
        self.assertEqual(router.fetch(date.today()), ())

    def test_league_only_does_not_fallback(self):
        router = SoccerProviderRouter("MLS", mode="league_only",
                                      fallback=lambda d: [match()])
        with self.assertRaises(ProviderUnavailable):
            router.fetch(date.today())

    def test_espn_only_does_not_call_primary(self):
        router = SoccerProviderRouter("MLS", mode="espn_only",
                                      primary=lambda d: self.fail("primary called"),
                                      fallback=lambda d: [match()])
        self.assertEqual(router.fetch(date.today()), (match(),))

    def test_cross_league_data_rejected(self):
        router = SoccerProviderRouter("MLS", mode="league_only",
                                      primary=lambda d: [match("NWSL")])
        with self.assertRaises(ProviderUnavailable):
            router.fetch(date.today())

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            SoccerProviderRouter("MLS", mode="random")

    def test_mls_native_match(self):
        rows = [{"matchId": "MLS-MAT-1", "homeTeamThreeLetterCode": "ATL",
                 "awayTeamThreeLetterCode": "MIA", "homeTeamGoals": 2,
                 "awayTeamGoals": 1, "matchStatus": "Live"}]
        parsed = parse_mls_matches(rows)
        self.assertEqual((parsed[0].home_id, parsed[0].status, parsed[0].home_score), ("ATL", "live", 2))
        self.assertEqual(parsed[0].goals, ())

    def test_nwsl_native_match(self):
        rows = [{"match_id": "N1", "home_team_id": "h", "away_team_id": "a",
                 "home_score_push": 1, "away_score_push": 0, "status": "Live"}]
        self.assertEqual(parse_nwsl_matches(rows)[0].status, "live")

    def test_unrecognized_native_shape_rejected(self):
        with self.assertRaises(ValueError):
            parse_mls_matches({"unexpected": []})

    def test_missing_nwsl_team_ids_rejected(self):
        with self.assertRaises(ValueError):
            parse_nwsl_matches([{"match_id": "N1", "status": "Live"}])


if __name__ == "__main__":
    unittest.main()
