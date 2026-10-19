"""Individual team color saves snapshot selected RGB values."""
import unittest
from universal_led import configurator


class TeamColorSaveTests(unittest.TestCase):
    def test_mlb_save_snapshots_and_validates_color(self):
        html=configurator.HTML
        body=html.split("document.getElementById('mlb-save-color').onclick=async()=>{",1)[1].split("document.getElementById('mlb-reset-color')",1)[0]
        self.assertIn('const color=clone(state.teams[code]);',body)
        self.assertIn('invalidColorEntry({teams:{[code]:color}})',body)
        self.assertIn('body:JSON.stringify({[code]:color})',body)
        self.assertIn('saved.teams[code]=color;markDirty()',body)

    def test_nhl_save_snapshots_and_validates_color(self):
        html=configurator.HTML
        body=html.split("document.getElementById('nhl-save-color').onclick=async()=>{",1)[1].split('const NHL_TEAMS=',1)[0]
        self.assertIn('const color=[...(nhlColors[code]||[])];',body)
        self.assertIn('invalidColorEntry({teams:{[code]:color}})',body)
        self.assertIn('body:JSON.stringify({[code]:color})',body)


if __name__=='__main__':
    unittest.main()
