import unittest

from universal_led.soccer import SoccerGoal, SoccerMatch
from universal_led.soccer_pixels import render_soccer_screen
from universal_led.soccer_screens import goal_screen, match_screen


class SoccerPixelTests(unittest.TestCase):
    def match(self, league="MLS"):
        return SoccerMatch("game-1", league, "ATL", "MIA", 2, 1, "live")

    def test_match_frame_is_64_by_32(self):
        frame = render_soccer_screen(match_screen(self.match()))
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_match_frame_contains_colored_pixels(self):
        frame = render_soccer_screen(match_screen(self.match()))
        self.assertTrue(any(pixel != (0, 0, 0) for row in frame.pixels for pixel in row))

    def test_goal_frame_is_64_by_32(self):
        screen = goal_screen(self.match(), SoccerGoal("goal-1", "ATL", "A. Forward", "67'"))
        frame = render_soccer_screen(screen)
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_long_name_and_punctuation_do_not_crash_renderer(self):
        screen = goal_screen(self.match(), SoccerGoal("goal-2", "ATL", "D'Angelo-Smith, Jr.", "90+3'"))
        frame = render_soccer_screen(screen)
        self.assertEqual(len(frame.ppm().split(b"\\n", 3)[-1]), 64 * 32 * 3)

    def test_nwsl_uses_same_pixel_renderer(self):
        frame = render_soccer_screen(match_screen(self.match("NWSL")))
        self.assertEqual(frame.width, 64)

    def test_unknown_characters_do_not_crash(self):
        screen = goal_screen(self.match(), SoccerGoal("goal-3", "ATL", "José García"))
        self.assertEqual(render_soccer_screen(screen).height, 32)


if __name__ == "__main__":
    unittest.main()
