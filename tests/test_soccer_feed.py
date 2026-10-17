import unittest

from universal_led.soccer_feed import parse_scoreboard


def fixture(details=None):
    return {"events": [{
        "id": "game-123",
        "status": {"type": {"state": "in"}},
        "competitions": [{
            "competitors": [
                {"homeAway": "home", "team": {"abbreviation": "ATL"}, "score": "2"},
                {"homeAway": "away", "team": {"abbreviation": "MIA"}, "score": "1"},
            ],
            "details": details or [],
        }],
    }]}


class SoccerFeedTests(unittest.TestCase):
    def test_mls_score_and_status(self):
        match, = parse_scoreboard(fixture(), "MLS")
        self.assertEqual((match.home_id, match.away_id, match.home_score, match.away_score), ("ATL", "MIA", 2, 1))
        self.assertEqual(match.status, "in")

    def test_long_form_live_status_prioritized(self):
        from universal_led.soccer_rotation import is_live
        for name in ("STATUS_IN_PROGRESS", "STATUS_HALFTIME", "STATUS_END_PERIOD"):
            payload = fixture()
            payload["events"][0]["status"]["type"] = {"name": name}
            game, = parse_scoreboard(payload, "MLS")
            self.assertTrue(is_live(game), name)

    def test_long_form_scheduled_and_final_status(self):
        from universal_led.soccer_rotation import is_live
        for name, expected in (("STATUS_SCHEDULED", "pre"), ("STATUS_FINAL", "post"),
                               ("STATUS_FULL_TIME", "post")):
            payload = fixture()
            payload["events"][0]["status"]["type"] = {"name": name}
            game, = parse_scoreboard(payload, "NWSL")
            self.assertEqual(game.status, expected)
            self.assertFalse(is_live(game))

    def test_nwsl_uses_same_parser(self):
        match, = parse_scoreboard(fixture(), "NWSL")
        self.assertEqual(match.league, "NWSL")

    def test_credited_scorer_and_minute(self):
        detail = {"id": "goal-1", "scoringPlay": True, "team": {"abbreviation": "ATL"},
                  "clock": {"displayValue": "67'"}, "athletesInvolved": [
                      {"type": "scorer", "athlete": {"displayName": "A. Forward"}},
                      {"type": "assist", "athlete": {"displayName": "B. Midfielder"}}]}
        match, = parse_scoreboard(fixture([detail]), "MLS")
        self.assertEqual((match.goals[0].scorer, match.goals[0].minute), ("A. Forward", "67'"))

    def test_assist_not_mistaken_for_scorer(self):
        detail = {"id": "goal-2", "scoringPlay": True, "athletesInvolved": [
            {"type": "assist", "athlete": {"displayName": "Not the scorer"}}]}
        match, = parse_scoreboard(fixture([detail]), "MLS")
        self.assertIsNone(match.goals[0].scorer)

    def test_own_goal_preserved(self):
        detail = {"id": "goal-3", "scoringPlay": True, "ownGoal": True}
        match, = parse_scoreboard(fixture([detail]), "NWSL")
        self.assertTrue(match.goals[0].own_goal)

    def test_non_scoring_events_ignored(self):
        match, = parse_scoreboard(fixture([{"id": "shot-1", "scoringPlay": False}]), "MLS")
        self.assertEqual(match.goals, ())

    def test_incomplete_competition_skipped(self):
        self.assertEqual(parse_scoreboard({"events": [{"id": "x", "competitions": []}]}, "MLS"), ())

    def test_malformed_event_does_not_discard_valid_match(self):
        payload = fixture()
        payload["events"].insert(0, None)
        payload["events"].insert(1, {"competitions": [None]})
        games = parse_scoreboard(payload, "MLS")
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0].match_id, "game-123")

    def test_malformed_competitor_is_ignored(self):
        payload = fixture()
        payload["events"][0]["competitions"][0]["competitors"].insert(0, None)
        match, = parse_scoreboard(payload, "NWSL")
        self.assertEqual((match.home_id, match.away_id), ("ATL", "MIA"))

    def test_malformed_scoring_detail_and_athlete_ignored(self):
        detail = {"id": "g1", "scoringPlay": True, "athletesInvolved": [None, {"type": None}]}
        match, = parse_scoreboard(fixture([None, detail]), "MLS")
        self.assertEqual(len(match.goals), 1)
        self.assertIsNone(match.goals[0].scorer)

    def test_unsupported_league_rejected(self):
        with self.assertRaises(ValueError):
            parse_scoreboard(fixture(), "EFL")


if __name__ == "__main__":
    unittest.main()
