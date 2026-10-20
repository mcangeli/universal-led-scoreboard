"""Favorite-only game mode warns when no favorites are selected."""
import unittest
from universal_led import configurator


class FavoriteModeWarningsTests(unittest.TestCase):
    def test_empty_favorites_warning_is_specific_to_favorites_only(self):
        html=configurator.HTML
        self.assertIn("favorites===0&&select.value==='favorite'",html)
        self.assertIn('No favorites selected, so this mode will have no matching games.',html)

    def test_favorite_changes_refresh_mode_explanation(self):
        html=configurator.HTML
        self.assertIn("event.target.closest('#favorite-teams,#nhl-teams,#nba-teams,#wnba-teams,#nfl-teams,#mls-teams,#nwsl-teams,#english-teams')",html)

    def test_mlb_required_favorite_message_matches_server_validation(self):
        html=configurator.HTML
        self.assertIn('MLB requires at least one favorite team, even when MLB is disabled.',html)


if __name__=='__main__':
    unittest.main()
