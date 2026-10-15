import unittest
from dataclasses import replace
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen


class MLBClassicLiveParityTests(unittest.TestCase):
    def test_count_appears_when_available(self):
        base=BaseballGame(status='live',balls=None,strikes=None)
        with_count=replace(base,balls=2,strikes=1)
        plain=MLBPaletteScreen(base).render()
        counted=MLBPaletteScreen(with_count).render()
        self.assertNotEqual(
            [[plain.pixels[y][x] for x in range(32,44)] for y in range(27,32)],
            [[counted.pixels[y][x] for x in range(32,44)] for y in range(27,32)])

    def test_unknown_count_does_not_show_zero_zero(self):
        game=BaseballGame(status='live',balls=None,strikes=None)
        frame=MLBPaletteScreen(game).render()
        self.assertTrue(all(frame.pixels[y][x]==(0,0,0)
                            for y in range(27,32) for x in range(32,44)))

    def test_outs_are_outlined_when_empty_and_filled_when_recorded(self):
        game=BaseballGame(status='live',outs=1)
        frame=MLBPaletteScreen(game).render()
        self.assertNotEqual(frame.pixels[28][20],(0,0,0))
        self.assertEqual(frame.pixels[28][24],(0,0,0))
        self.assertNotEqual(frame.pixels[27][23],(0,0,0))

    def test_count_stays_visible_in_double_digit_inning(self):
        game=BaseballGame(status='live',inning=12,balls=3,strikes=2)
        frame=MLBPaletteScreen(game).render()
        self.assertTrue(any(frame.pixels[y][x]!=(0,0,0)
                            for y in range(27,32) for x in range(32,44)))


if __name__=='__main__':
    unittest.main()
