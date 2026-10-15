import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_live_details import compact_name, visible_name, MLBLiveDetailsScreen


class MatchupNameTests(unittest.TestCase):
    def test_preserves_surname_particles(self):
        self.assertEqual(compact_name('Juan De La Cruz'),'DE LA CRUZ')
        self.assertEqual(compact_name('Alex van Dijk'),'VAN DIJK')

    def test_long_surnames_scroll_instead_of_truncating(self):
        name='VERY-LONG-HYPHENATED-NAME'
        self.assertEqual(compact_name(name),name)
        self.assertEqual(len(visible_name(name,0)),13)
        self.assertNotEqual(visible_name(name,0),visible_name(name,5))

    def test_short_names_do_not_scroll(self):
        self.assertEqual(visible_name('Max Fried',0),visible_name('Max Fried',99))
        self.assertEqual(visible_name(None,12),'TBD')

    def test_matchup_frame_remains_bounded(self):
        game=BaseballGame(pitcher='Juan Very-Long-Hyphenated-Name',
                          batter='Someone Van Der Verylongname',
                          pitch_count=123,pitch_speed_mph=101,balls=3,strikes=2)
        for offset in (0,7,1000):
            frame=MLBLiveDetailsScreen(game,offset=offset).render()
            self.assertEqual((frame.width,frame.height),(64,32))
            self.assertTrue(any(pixel!=(0,0,0) for pixel in frame.pixels[27]))


if __name__=='__main__':
    unittest.main()
