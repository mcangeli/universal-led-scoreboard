import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen
from universal_led.mlb_data import parse_schedule


class InningBreakTests(unittest.TestCase):
    def test_middle_and_end_hide_stale_live_indicators(self):
        for state in ('Middle','End'):
            with self.subTest(state=state):
                game=BaseballGame(status='live',inning=8,inning_state=state,
                                  outs=2,balls=3,strikes=2,bases=(True,True,True))
                fb=MLBPaletteScreen(game).render()
                self.assertTrue(any(fb.pixels[y][x]!=(0,0,0)
                                    for y in range(27,32) for x in range(2,30)))
                self.assertTrue(all(fb.pixels[y][x]==(0,0,0)
                                    for y in range(27,32) for x in range(32,64)))

    def test_normal_live_footer_still_shows_runners(self):
        game=BaseballGame(status='live',inning_state='Bottom',bases=(True,False,False))
        fb=MLBPaletteScreen(game).render()
        self.assertNotEqual(fb.pixels[30][55],(0,0,0))

    def test_schedule_passes_through_inning_state(self):
        payload={'dates':[{'games':[{
            'status':{'abstractGameState':'Live'},
            'teams':{'away':{'team':{'id':144}},'home':{'team':{'id':121}}},
            'linescore':{'currentInning':5,'inningState':'Middle','isTopInning':True}
        }]}]}
        games=parse_schedule(payload)
        self.assertEqual(games[0].inning_state,'Middle')


if __name__=='__main__':
    unittest.main()
