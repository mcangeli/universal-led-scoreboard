"""English favorite IDs survive abbreviation changes and division moves."""
import unittest

from universal_led.soccer import SoccerMatch
from universal_led.soccer_feed import parse_scoreboard
from universal_led.soccer_rotation import eligible_matches, prioritize_live


def event(team_id, abbreviation, state="pre"):
    return {"events": [{"id": "match", "status": {"type": {"state": state}},
            "competitions": [{"competitors": [
                {"homeAway": "home", "team": {"id": team_id, "abbreviation": abbreviation}, "score": "1"},
                {"homeAway": "away", "team": {"id": "200", "abbreviation": "OPP"}, "score": "0"}]}]}]}


class EnglishFavoriteRotationTests(unittest.TestCase):
    def test_stable_favorite_across_divisions(self):
        first = parse_scoreboard(event("381", "WRX"), "CHAMPIONSHIP")
        second = parse_scoreboard(event("381", "WXM"), "EPL")
        for games in (first, second):
            self.assertEqual(len(eligible_matches(games, favorites=("espn:381",), mode="favorites")), 1)

    def test_english_display_keeps_abbreviation(self):
        match = parse_scoreboard(event("381", "WRX"), "EPL")[0]
        self.assertEqual(match.home_id, "WRX")
        self.assertEqual(match.home_club_key, "espn:381")

    def test_missing_provider_id_does_not_invent_key(self):
        match = parse_scoreboard(event("", "WRX"), "EPL")[0]
        self.assertIsNone(match.home_club_key)

    def test_existing_mls_abbreviation_favorite(self):
        match = parse_scoreboard(event("381", "ATL"), "MLS")[0]
        self.assertIsNone(match.home_club_key)
        self.assertEqual(len(eligible_matches((match,), favorites=("ATL",), mode="favorites")), 1)

    def test_live_games_win_across_english_divisions(self):
        scheduled = parse_scoreboard(event("381", "WRX"), "CHAMPIONSHIP")[0]
        live = parse_scoreboard(event("9", "CFC", "in"), "EPL")[0]
        self.assertEqual(prioritize_live((scheduled, live)), (live,))

    def test_favorite_filter_does_not_change_live_status(self):
        scheduled = parse_scoreboard(event("381", "WRX"), "CHAMPIONSHIP")[0]
        live = parse_scoreboard(event("9", "CFC", "in"), "EPL")[0]
        selected = eligible_matches((scheduled, live), favorites=("espn:381",), mode="favorites")
        self.assertEqual(selected, (scheduled,))


if __name__ == "__main__":
    unittest.main()
