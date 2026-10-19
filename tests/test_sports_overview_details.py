"""Sports overview keeps saved favorites distinct from game coverage."""
import unittest
from universal_led import configurator


class SportsOverviewDetailTests(unittest.TestCase):
    def test_saved_favorites_count_is_visible(self):
        html=configurator.HTML
        self.assertIn("const favorites=(sport.favorite_teams||[]).length",html)
        self.assertIn("favorites+' favorite'+(favorites===1?'':'s')",html)

    def test_english_game_divisions_are_distinct_from_favorites(self):
        html=configurator.HTML
        self.assertIn("(sport.enabled_leagues||[]).length+' game division(s)'",html)
        self.assertIn("document.getElementById('sport-state-'+name).textContent=details.join(' · ')",html)


if __name__=='__main__':
    unittest.main()
