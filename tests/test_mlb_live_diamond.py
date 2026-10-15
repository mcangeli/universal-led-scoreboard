"""Pixel-level assertions for the 64x32 live-game footer."""
import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen

COLORS={'text':(1,2,3),'dim':(4,5,6),'accent':(7,8,9),
        'error':(10,11,12),'separator':(13,14,15)}


class LiveDiamondTests(unittest.TestCase):
    def test_occupied_bases_are_diamonds_in_correct_positions(self):
        positions=((55,30),(50,28),(45,30))
        for base in range(3):
            with self.subTest(base=base):
                occupied=tuple(index==base for index in range(3))
                fb=MLBPaletteScreen(BaseballGame(bases=occupied),scoreboard_colors=COLORS).render()
                for index,(x,y) in enumerate(positions):
                    expected=COLORS['accent'] if index==base else COLORS['dim']
                    for dx,dy in ((0,-1),(-1,0),(0,0),(1,0),(0,1)):
                        self.assertEqual(fb.pixels[y+dy][x+dx],expected)

    def test_out_lamps_have_distinct_on_off_states(self):
        for outs in range(4):
            with self.subTest(outs=outs):
                fb=MLBPaletteScreen(BaseballGame(outs=outs),scoreboard_colors=COLORS).render()
                for index in range(3):
                    expected=COLORS['error'] if index<outs else COLORS['dim']
                    x=19+index*4
                    # All lamps have a visible outline; only recorded outs fill the center.
                    for dx,dy in ((0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2)):
                        self.assertEqual(fb.pixels[27+dy][x+dx],expected)
                    self.assertEqual(fb.pixels[28][x+1],
                                     COLORS['error'] if index<outs else (0,0,0))

    def test_final_footer_does_not_show_live_bases(self):
        fb=MLBPaletteScreen(BaseballGame(status='final',bases=(True,True,True)),
                            scoreboard_colors=COLORS).render()
        for x,y in ((55,30),(50,28),(45,30)):
            self.assertEqual(fb.pixels[y][x],(0,0,0))


if __name__=='__main__':
    unittest.main()
