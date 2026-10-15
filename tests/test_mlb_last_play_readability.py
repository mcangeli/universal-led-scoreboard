import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_previous_play import MLBPreviousPlayScreen


class LastPlayReadabilityTests(unittest.TestCase):
    def test_short_description_visible_immediately(self):
        game=BaseballGame(previous_play='SINGLE')
        frame=MLBPreviousPlayScreen(game,offset=0).render()
        self.assertTrue(any(frame.pixels[y][x]!=(0,0,0)
                            for y in range(12,17) for x in range(0,24)))

    def test_short_description_does_not_scroll_off_screen(self):
        game=BaseballGame(previous_play='SINGLE')
        first=MLBPreviousPlayScreen(game,offset=0).render()
        later=MLBPreviousPlayScreen(game,offset=500).render()
        self.assertEqual(first.pixels,later.pixels)

    def test_long_description_scrolls_and_clamps(self):
        game=BaseballGame(previous_play='BATTER HITS A DOUBLE INTO LEFT FIELD AND TWO RUNNERS SCORE')
        first=MLBPreviousPlayScreen(game,offset=0).render()
        later=MLBPreviousPlayScreen(game,offset=12).render()
        self.assertNotEqual(first.pixels,later.pixels)
        last=MLBPreviousPlayScreen(game,offset=500).render()
        beyond=MLBPreviousPlayScreen(game,offset=1000).render()
        self.assertEqual(last.pixels,beyond.pixels)


if __name__=='__main__':
    unittest.main()
