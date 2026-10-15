import unittest
from universal_led.news_screen import headline_page, NewsHeadlineScreen
from universal_led.mlb_previous_play import wrap_play


class NewsHeadlinePagingTests(unittest.TestCase):
    def test_long_headline_advances_and_wraps(self):
        text='THE ATLANTA BRAVES WIN ANOTHER IMPORTANT BASEBALL GAME IN EXTRA INNINGS'
        lines=wrap_play(text,16)
        self.assertGreater(len(lines),3)
        self.assertEqual(headline_page(text,0),lines[:2])
        self.assertEqual(headline_page(text,16),lines[1:3])
        self.assertEqual(headline_page(text,16*(len(lines)-1)),lines[:2])

    def test_short_headline_stays_put(self):
        self.assertEqual(headline_page('BRAVES WIN',1000),['BRAVES WIN',''])

    def test_render_changes_on_page_boundary(self):
        text='THE ATLANTA BRAVES WIN ANOTHER IMPORTANT BASEBALL GAME IN EXTRA INNINGS'
        self.assertNotEqual(NewsHeadlineScreen(text,offset=0).render().pixels,
                            NewsHeadlineScreen(text,offset=16).render().pixels)


if __name__=='__main__':
    unittest.main()
