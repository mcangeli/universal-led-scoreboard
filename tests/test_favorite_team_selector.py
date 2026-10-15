import re
import unittest
from html import unescape
from universal_led.configurator import HTML
from universal_led.mlb_data import TEAM_ABBREVIATIONS


class FavoriteTeamSelectorTests(unittest.TestCase):
    def test_full_mlb_team_list_in_select(self):
        match=re.search(r'<select id="favorite"[^>]*>(.*?)</select>',HTML,re.S)
        self.assertIsNotNone(match)
        options=re.findall(r'<option value="([A-Z]{3})"[^>]*>(.*?)</option>',match.group(1))
        self.assertEqual(len(options),30)
        self.assertEqual({code for code,_ in options},set(TEAM_ABBREVIATIONS.values()))
        self.assertEqual(dict(options)['ATL'],'Atlanta Braves')
        self.assertEqual(dict(options)['SFG'],'San Francisco Giants')

    def test_favorite_value_is_still_saved_as_feed_identifier(self):
        self.assertIn("document.getElementById('favorite').value=mlb.favorite_team",HTML)
        self.assertIn("next.mlb.favorite_team=document.getElementById('favorite').value.trim().toUpperCase()",HTML)

    def test_team_selector_is_accessibly_labeled(self):
        self.assertIn('<label for="favorite">Favorite MLB team</label>',HTML)


if __name__=='__main__':
    unittest.main()
