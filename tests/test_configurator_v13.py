import unittest
from universal_led.configurator import HTML,make_handler
from universal_led.colors import TEAM_COLORS,DEFAULT_SCOREBOARD
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen

class ConfiguratorV13Tests(unittest.TestCase):
    def test_editor_controls(self):
        for marker in ('preview-team','dirty','cancel','reset','Unsaved changes','api/defaults'):
            with self.subTest(marker=marker):
                self.assertIn(marker,HTML)
    def test_palette_defaults_available(self):
        self.assertIn('ATL',TEAM_COLORS)
        self.assertIn('accent',DEFAULT_SCOREBOARD)
    def test_team_preview_can_render_offseason(self):
        teams=dict(TEAM_COLORS)
        teams['ATL']=(1,255,2)
        game=BaseballGame(away='NYM',home='ATL')
        frame=MLBPaletteScreen(game,teams,dict(DEFAULT_SCOREBOARD)).render()
        self.assertIn((1,255,2),frame.pixels[17])
    def test_handler_exists(self):
        self.assertTrue(make_handler('/tmp','token'))
if __name__=='__main__':
    unittest.main()
