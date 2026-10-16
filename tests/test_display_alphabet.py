import unittest

from universal_led.display import FONT, Framebuffer


class DisplayAlphabetTests(unittest.TestCase):
    def test_all_uppercase_letters_supported(self):
        self.assertTrue(set('ABCDEFGHIJKLMNOPQRSTUVWXYZ').issubset(FONT))
        frame = Framebuffer(200, 8)
        frame.text('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 0, 0, (255, 255, 255))

    def test_mlb_team_abbreviations(self):
        frame = Framebuffer(64, 32)
        for team in ('PHI', 'ATL', 'NYM', 'LAD', 'CHC', 'BOS', 'WSH', 'TEX'):
            with self.subTest(team=team):
                frame.text(team, 0, 0, (255, 255, 255))


if __name__ == '__main__':
    unittest.main()
