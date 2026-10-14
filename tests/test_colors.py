import json
import tempfile
import unittest
from pathlib import Path
from universal_led.colors import parse_rgb,normalize_team_colors,load_palette
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_colored import MLBColoredScreen

class ColorTests(unittest.TestCase):
    def test_rgb(self):
        self.assertEqual(parse_rgb('#cc2036'),(204,32,54))
        self.assertEqual(parse_rgb([1,2,3]),(1,2,3))
    def test_invalid_rgb(self):
        for value in ('red','#gg0000',[1,2,256],[True,2,3]):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): parse_rgb(value)
    def test_team_override(self):
        self.assertEqual(normalize_team_colors({'ATL':{'primary':'#123456'}})['ATL'],(18,52,86))
    def test_load_files(self):
        with tempfile.TemporaryDirectory() as directory:
            t=Path(directory)/'teams.json'
            s=Path(directory)/'scoreboard.json'
            t.write_text(json.dumps({'ATL':'#123456'}))
            s.write_text(json.dumps({'accent':[4,5,6]}))
            teams,board=load_palette(t,s)
            self.assertEqual(teams['ATL'],(18,52,86))
            self.assertEqual(board['accent'],(4,5,6))
            fb=MLBColoredScreen(BaseballGame(),teams,board).render()
            self.assertIn((18,52,86),fb.pixels[17])
            self.assertIn((4,5,6),fb.pixels[1])
    def test_dimensions(self):
        f=MLBColoredScreen().render()
        self.assertEqual((f.width,f.height),(64,32))
if __name__=='__main__':
    unittest.main()
