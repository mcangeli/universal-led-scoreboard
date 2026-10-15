import unittest
from universal_led.mlb_previous_play import wrap_play,visible_play_lines


class PlayWordWrappingTests(unittest.TestCase):
    def test_words_stay_together(self):
        self.assertEqual(wrap_play('Ronald Acuna singles to center field'),[
            'RONALD ACUNA','SINGLES TO','CENTER FIELD'])

    def test_two_rows_appear_without_scroll(self):
        self.assertEqual(visible_play_lines('Batter walks',0),['BATTER WALKS',''])

    def test_scrolling_advances_by_complete_rows(self):
        text='Ronald Acuna singles to center field'
        self.assertEqual(visible_play_lines(text,0),['RONALD ACUNA','SINGLES TO'])
        self.assertEqual(visible_play_lines(text,13),['SINGLES TO','CENTER FIELD'])
        self.assertEqual(visible_play_lines(text,999),['SINGLES TO','CENTER FIELD'])

    def test_overlong_word_splits_only_when_necessary(self):
        lines=wrap_play('ABCDEFGHIJKLMNOPQRSTUV')
        self.assertEqual(lines,['ABCDEFGHIJKLMNOP','QRSTUV'])

    def test_empty_description_has_fallback(self):
        self.assertEqual(visible_play_lines('',0),['NO PLAY DATA',''])


if __name__=='__main__':
    unittest.main()
