import re
import unittest
from universal_led.configurator import HTML


class FavoriteTeamSelectorTests(unittest.TestCase):
    def test_all_30_mlb_teams_have_checkboxes(self):
        mlb_section=HTML.split('<div id="favorite-teams" class="favorite-team-grid">',1)[1].split('</div>',1)[0]
        options=re.findall(r'<input type="checkbox" value="([A-Z]{3})"> ([^<]+)',mlb_section)
        self.assertEqual(len(options),30)
        self.assertEqual(len({code for code,_ in options}),30)
        self.assertEqual(dict(options)['ATL'],'Atlanta Braves')
        self.assertEqual(dict(options)['SFG'],'San Francisco Giants')

    def test_favorites_are_loaded_and_saved_as_list(self):
        self.assertIn('setFavoriteTeams(mlb.favorite_teams)',HTML)
        self.assertIn('next.mlb.favorite_teams=getFavoriteTeams()',HTML)

    def test_selector_has_accessible_summary(self):
        self.assertIn('id="favorite-summary"',HTML)
        self.assertIn('aria-live="polite"',HTML)


if __name__=='__main__':
    unittest.main()
