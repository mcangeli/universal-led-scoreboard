import unittest

from universal_led.soccer import SoccerMatch
from universal_led.soccer_rotation import eligible_matches, is_live, prioritize_live


def match(league="MLS", home="ATL", away="MIA", status="in"):
    return SoccerMatch("id-" + home, league, home, away, 1, 0, status)


class SoccerRotationTests(unittest.TestCase):
    def test_espn_live_state(self):
        self.assertTrue(is_live(match(status="in")))

    def test_explicit_live_state(self):
        self.assertTrue(is_live(match(status="live")))

    def test_final_not_live(self):
        self.assertFalse(is_live(match(status="post")))

    def test_live_games_hide_scheduled_games(self):
        scheduled = match(status="pre")
        live = match(home="NY", status="in")
        self.assertEqual(prioritize_live([scheduled, live]), (live,))

    def test_no_live_games_retains_scheduled_and_final(self):
        games = [match(status="pre"), match(home="NY", status="post")]
        self.assertEqual(prioritize_live(games), tuple(games))

    def test_favorites_match_home_or_away(self):
        games = [match(), match(home="NY", away="SEA")]
        self.assertEqual(eligible_matches(games, favorites=["sea"], mode="favorites"), (games[1],))

    def test_favorites_match_padded_home_identifier(self):
        game = match(home=" atl ")
        self.assertEqual(eligible_matches([game], favorites=["ATL"], mode="favorites"), (game,))

    def test_favorites_match_padded_away_identifier(self):
        game = match(away=" mia ")
        self.assertEqual(eligible_matches([game], favorites=["MIA"], mode="favorites"), (game,))

    def test_favorites_mode_without_selected_teams_shows_all(self):
        games = [match(), match(home="NY")]
        self.assertEqual(eligible_matches(games, favorites=[], mode="favorites"), tuple(games))

    def test_fallback_mode_without_selected_teams_shows_all(self):
        games = [match(), match(home="NY")]
        self.assertEqual(eligible_matches(games, favorites=[], mode="fallback"), tuple(games))

    def test_favorites_only_no_match_returns_empty(self):
        self.assertEqual(eligible_matches([match()], favorites=["NY"], mode="favorites"), ())

    def test_fallback_uses_all_when_no_favorites(self):
        games = [match()]
        self.assertEqual(eligible_matches(games, favorites=["NY"], mode="fallback"), tuple(games))

    def test_fallback_prefers_favorite_games(self):
        games = [match(), match(home="NY")]
        self.assertEqual(eligible_matches(games, favorites=["NY"], mode="fallback"), (games[1],))

    def test_leagues_can_be_mixed(self):
        games = [match(), match(league="NWSL", home="POR")]
        self.assertEqual(prioritize_live(games), tuple(games))

    def test_unknown_mode_rejected(self):
        with self.assertRaises(ValueError):
            eligible_matches([match()], mode="guess")


if __name__ == "__main__":
    unittest.main()
