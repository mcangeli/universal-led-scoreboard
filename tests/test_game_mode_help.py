"""Game selection mode explanations remain consistent across sports."""
import unittest
from universal_led import configurator


class GameModeHelpTests(unittest.TestCase):
    def test_every_game_mode_has_contextual_help(self):
        html=configurator.HTML
        for name in ('mode','nhl-mode','nba-mode','wnba-mode','nfl-mode','mls-mode','nwsl-mode','english-mode'):
            with self.subTest(sport=name):
                self.assertIn('id="'+name+'-help"',html)

    def test_help_updates_on_selection_and_settings_reload(self):
        html=configurator.HTML
        self.assertIn('function refreshGameSelectionHelp()',html)
        self.assertIn('if(event.target.matches(',html)
        self.assertIn('refreshGameSelectionHelp();\n refreshSportsOverview()',html)

    def test_all_modes_have_distinct_explanations(self):
        html=configurator.HTML
        self.assertIn("favorite:'Only games involving selected favorite teams",html)
        self.assertIn("fallback:'Show favorite-team games when available",html)
        self.assertIn("all:'Show all games in the selected coverage",html)


if __name__=='__main__':
    unittest.main()
