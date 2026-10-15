import unittest

from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_data import parse_schedule


def fixture(linescore):
    return {'dates':[{'games':[{
        'teams':{'away':{'team':{'id':144}},'home':{'team':{'id':119}}},
        'status':{'abstractGameState':'Live','detailedState':'In Progress'},
        'linescore':linescore,
    }]}]}


class MLBLiveDetailsTests(unittest.TestCase):
    def test_extracts_live_count_and_matchup(self):
        ls={'balls':3,'strikes':2,
            'offense':{'batter':{'fullName':'Ronald Acuna Jr.'}},
            'defense':{'pitcher':{'fullName':'Clayton Kershaw'}}}
        game=parse_schedule(fixture(ls))[0]
        self.assertEqual((game.balls,game.strikes),(3,2))
        self.assertEqual(game.batter,'Ronald Acuna Jr.')
        self.assertEqual(game.pitcher,'Clayton Kershaw')

    def test_missing_live_details_are_unknown(self):
        game=parse_schedule(fixture({}))[0]
        self.assertIsNone(game.balls)
        self.assertIsNone(game.strikes)
        self.assertIsNone(game.pitcher)
        self.assertIsNone(game.batter)

    def test_malformed_counts_do_not_break_feed(self):
        game=parse_schedule(fixture({'balls':'unknown','strikes':-4}))[0]
        self.assertIsNone(game.balls)
        self.assertIsNone(game.strikes)

    def test_model_rejects_invalid_counts(self):
        for kwargs in ({'balls':-1},{'balls':5},{'strikes':4},
                       {'pitch_count':-1},{'pitch_speed_mph':-1}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                BaseballGame(**kwargs)


if __name__=='__main__':
    unittest.main()
