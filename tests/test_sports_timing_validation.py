"""Guard client-side sports timing validation against server bounds."""
import unittest
from universal_led import configurator


class SportsTimingValidationTests(unittest.TestCase):
    def test_all_eight_sports_are_checked_before_save(self):
        html=configurator.HTML
        self.assertIn("for(const sport of ['mlb','nhl','nba','wnba','nfl','mls','nwsl','english'])",html)
        self.assertIn("for(const field of ['rotation','refresh'])",html)
        self.assertIn('const timingError=validateSportTiming()',html)

    def test_bounds_match_backend_and_focus_invalid_field(self):
        html=configurator.HTML
        self.assertIn("const minimum=sport==='mlb'?1:5",html)
        self.assertIn('value>3600',html)
        self.assertIn('input.focus()',html)
        self.assertIn("if(timingError){status.textContent=timingError;return;}",html)


if __name__=='__main__':
    unittest.main()
