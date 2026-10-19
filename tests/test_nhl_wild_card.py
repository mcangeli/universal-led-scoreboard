import unittest
from universal_led.nhl_standings_feed import parse_nhl_wild_card, fetch_nhl_wild_card


def team(conf, division_rank, conference_rank, code):
    return {'conferenceName': conf, 'divisionSequence': division_rank,
            'conferenceSequence': conference_rank, 'teamAbbrev': {'default': code},
            'wins': 30, 'losses': 20, 'otLosses': 5,
            'gamesPlayed': 55, 'points': 65}


class NHLWildCardTests(unittest.TestCase):
    def test_division_qualifiers_excluded_and_five_per_conference(self):
        data = {'standings': []}
        for conf in ('Eastern', 'Western'):
            data['standings'].append(team(conf, 2, 1, conf[:1] + 'A'))
            data['standings'].extend(team(conf, 4 + i, i + 2, conf[:1] + str(i))
                                     for i in range(7))
        rows = parse_nhl_wild_card(data)
        self.assertEqual(len(rows), 10)
        self.assertEqual([r.rank for r in rows[:5]], [1, 2, 3, 4, 5])
        self.assertTrue(all(r.group == 'Eastern_Wild_Card' for r in rows[:5]))
        self.assertTrue(all(r.group == 'Western_Wild_Card' for r in rows[5:]))

    def test_official_conference_order_overrides_input_order(self):
        data = {'standings': [team('Eastern', 4, 9, 'NYI'),
                              team('Eastern', 5, 7, 'OTT')]}
        self.assertEqual([r.team_id for r in parse_nhl_wild_card(data)], ['OTT', 'NYI'])

    def test_invalid_response_rejected(self):
        with self.assertRaises(ValueError):
            parse_nhl_wild_card({})

    def test_group_selection(self):
        rows = parse_nhl_wild_card({'standings': [team('Western', 4, 9, 'STL')]})
        selected = fetch_nhl_wild_card('Western_Wild_Card', fetcher=lambda: rows)
        self.assertEqual(len(selected), 1)
        with self.assertRaises(ValueError):
            fetch_nhl_wild_card('invalid', fetcher=lambda: rows)


if __name__ == '__main__':
    unittest.main()
