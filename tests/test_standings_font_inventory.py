"""Standings font inventory and glyph integrity checks."""
import string
import unittest

from universal_led.display import Framebuffer
from universal_led.standings_screen import TINY, WHITE, _tiny_text


class StandingsFontTests(unittest.TestCase):
    def test_complete_basic_scoreboard_character_set(self):
        required = set(string.ascii_uppercase + string.digits +
                       " -.,:/+%'&()?!#=*_")
        self.assertFalse(required - set(TINY))

    def test_all_glyphs_have_exactly_three_by_five_bits(self):
        for char, glyph in TINY.items():
            with self.subTest(char=char):
                self.assertEqual(len(glyph), 5)
                self.assertTrue(all(len(line) == 3 and set(line) <= {'0', '1'}
                                    for line in glyph))

    def test_decimal_and_separator_are_not_blank(self):
        for char in ('.', ',', ':', '/', '+', '%', '?'):
            with self.subTest(char=char):
                self.assertTrue(any('1' in line for line in TINY[char]))

    def test_unsupported_glyph_uses_visible_placeholder(self):
        unknown = Framebuffer(64, 32)
        expected = Framebuffer(64, 32)
        _tiny_text(unknown, '⚽', 0, 0, WHITE, 1)
        _tiny_text(expected, '?', 0, 0, WHITE, 1)
        self.assertEqual(unknown.pixels, expected.pixels)

    def test_lowercase_team_abbreviation_is_supported(self):
        lower = Framebuffer(64, 32)
        upper = Framebuffer(64, 32)
        _tiny_text(lower, 'atl', 0, 0, WHITE, 3)
        _tiny_text(upper, 'ATL', 0, 0, WHITE, 3)
        self.assertEqual(lower.pixels, upper.pixels)


if __name__ == '__main__':
    unittest.main()
