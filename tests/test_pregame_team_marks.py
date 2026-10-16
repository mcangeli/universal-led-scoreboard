"""Pregame pixel-art regression for the Guardians/Rays fixture."""
import unittest
from dataclasses import replace
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen
from universal_led.mlb_team_marks import SPRITE_COLORS


class PregameMarksTests(unittest.TestCase):
    def test_guardians_rays_marks_render_before_first_pitch(self):
        game=BaseballGame(away='CLE',home='TBR',status='pregame',
                          start_time='2026-10-16T23:00:00Z')
        frame=MLBPaletteScreen(game,pregame_page=0).render()
        # Marks are rendered at x=24 and y=6 (away), y=16 (home).
        guardians=set(SPRITE_COLORS['CLE'].values())
        rays=set(SPRITE_COLORS['TBR'].values())
        self.assertTrue(any(frame.pixels[y][x] in guardians
                            for y in range(6,15) for x in range(24,35)))
        self.assertTrue(any(frame.pixels[y][x] in rays
                            for y in range(16,25) for x in range(24,35)))

    def test_live_marks_remain_visible(self):
        game=BaseballGame(away='CLE',home='TBR',status='live')
        frame=MLBPaletteScreen(game).render()
        self.assertEqual(frame.pixels[6][26],SPRITE_COLORS['CLE']['R'])


if __name__=='__main__':
    unittest.main()
