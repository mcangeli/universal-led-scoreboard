"""Regression coverage for punctuation across shared compact text renderers."""
import unittest

from universal_led.display import Framebuffer
from universal_led.mlb_classic import SMALL, small
from universal_led.mlb_previous_play import sanitize_play, wrap_play
from universal_led.news_screen import NewsHeadlineScreen


class ApostropheRenderingTests(unittest.TestCase):
    def test_straight_and_curly_apostrophes_survive_sanitization(self):
        self.assertEqual(sanitize_play("TEAM'S WIN"), "TEAM'S WIN")
        self.assertEqual(sanitize_play("TEAM’S WIN"), "TEAM'S WIN")
        self.assertEqual(sanitize_play("‘TEAM’"), "'TEAM'")

    def test_wrapping_preserves_apostrophe_inside_word(self):
        self.assertIn("TEAM'S", " ".join(wrap_play("TEAM’S BIG WIN")))

    def test_compact_font_draws_apostrophe(self):
        self.assertIn("'", SMALL)
        frame = Framebuffer()
        small(frame, "'", 0, 0)
        self.assertTrue(any(pixel != (0, 0, 0) for row in frame.pixels for pixel in row))

    def test_large_font_accepts_curly_apostrophe(self):
        frame = Framebuffer()
        frame.text("TEAM’S", 0, 0, (255, 255, 255))
        self.assertTrue(any(pixel != (0, 0, 0) for row in frame.pixels for pixel in row))

    def test_news_headline_renders_curly_apostrophe(self):
        frame = NewsHeadlineScreen("TEAM’S BIG WIN", source="EDITOR’S PICK").render()
        self.assertEqual((frame.width, frame.height), (64, 32))


if __name__ == "__main__":
    unittest.main()
