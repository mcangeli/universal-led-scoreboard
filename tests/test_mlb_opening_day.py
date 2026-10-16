import unittest
from universal_led.mlb_opening_day import from_schedule

def game(when, away, home, kind='R'):
    return {'gameType': kind, 'gameDate': when,
            'teams': {'away': {'team': {'id': away}},
                      'home': {'team': {'id': home}}}}

class MLBOpeningDayTests(unittest.TestCase):
    def setUp(self):
        self.schedule = {'dates': [{'games': [
            game('2027-03-25T23:00:00Z', 144, 139, 'S'),
            game('2027-03-26T17:00:00Z', 119, 147),
            game('2027-03-27T18:00:00Z', 144, 114),
            game('2027-03-28T18:00:00Z', 139, 144),
        ]}]}

    def test_league_ignores_spring_training(self):
        result = from_schedule(self.schedule, 2027)
        self.assertEqual(result.starts_at.isoformat(), '2027-03-26T17:00:00+00:00')

    def test_favorite_first_game(self):
        result = from_schedule(self.schedule, 2027, target='favorite', team='ATL')
        self.assertEqual(result.starts_at.isoformat(), '2027-03-27T18:00:00+00:00')
        self.assertEqual(result.team, 'ATL')

    def test_missing_schedule_returns_none(self):
        self.assertIsNone(from_schedule({'dates': []}, 2027))
        self.assertIsNone(from_schedule(self.schedule, 2027, target='favorite', team='MIL'))

    def test_naive_or_invalid_dates_are_ignored(self):
        self.assertIsNone(from_schedule({'dates': [{'games': [
            game('2027-03-26T17:00:00', 144, 114),
            game('not-a-date', 144, 114),
        ]}]}, 2027))

    def test_invalid_favorite_rejected(self):
        with self.assertRaises(ValueError):
            from_schedule(self.schedule, 2027, target='favorite')

if __name__ == '__main__':
    unittest.main()
