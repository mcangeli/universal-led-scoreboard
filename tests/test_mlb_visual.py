import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_visual import MLBVisualScreen, TEAM_COLORS
from universal_led.mlb_data import parse_schedule

class VisualTests(unittest.TestCase):
    def test_colors_and_dimensions(self):
        f=MLBVisualScreen().render()
        self.assertEqual((f.width,f.height),(64,32))
        self.assertIn(TEAM_COLORS['ATL'],f.pixels[17])
        self.assertIn(TEAM_COLORS['NYM'],f.pixels[7])
    def test_statuses(self):
        for status in ('live','pregame','final','delayed','postponed'):
            with self.subTest(status=status):
                f=MLBVisualScreen(BaseballGame(status=status)).render()
                self.assertEqual(len(f.pixels),32)
    def test_api_interruptions(self):
        for detail,expected in [('Delayed Start','delayed'),('Postponed','postponed')]:
            payload={'dates':[{'games':[{'teams':{
                'away':{'team':{'abbreviation':'NYM'}},
                'home':{'team':{'abbreviation':'ATL'}}},
                'status':{'abstractGameState':'Preview','detailedState':detail}}]}]}
            self.assertEqual(parse_schedule(payload)[0].status,expected)
if __name__=='__main__':
    unittest.main()
