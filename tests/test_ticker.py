import unittest
from universal_led.ticker import TickerItem, normalize_items, active_item


class TickerTests(unittest.TestCase):
    def test_multiple_sports_share_one_ticker(self):
        items=[TickerItem('mlb','Braves win',priority=2),
               TickerItem('nhl','Overtime tonight',priority=1),
               TickerItem('weather','Clear skies',category='weather')]
        self.assertEqual([active_item(items,t,10).source for t in (0,10,20,30)],
                         ['mlb','nhl','weather','mlb'])

    def test_deduplicate_normalized_headlines(self):
        items=[TickerItem('MLB','Braves  win'),TickerItem('mlb',' braves win '),
               TickerItem('NHL','Braves win')]
        self.assertEqual(len(normalize_items(items)),2)

    def test_priority_and_limits(self):
        items=[TickerItem('a','low'),TickerItem('b','high',priority=5)]
        self.assertEqual(normalize_items(items,max_items=1)[0].source,'b')

    def test_empty_and_invalid_intervals(self):
        self.assertIsNone(active_item([],0))
        with self.assertRaises(ValueError):
            active_item([],0,0)
        with self.assertRaises(ValueError):
            TickerItem('mlb',' ')
        with self.assertRaises(ValueError):
            normalize_items([],max_items=0)


if __name__=='__main__':
    unittest.main()
