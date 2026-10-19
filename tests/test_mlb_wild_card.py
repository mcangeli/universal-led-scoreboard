import unittest

from universal_led.mlb_standings_feed import (
    parse_mlb_wild_card, fetch_mlb_wild_card, fetch_mlb_wild_card_group)


class MLBWildCardTests(unittest.TestCase):
    def setUp(self):
        self.payload = {'records': [
            {'league': {'id': 103}, 'teamRecords': [
                {'team': {'id': 144}, 'wins': 80, 'losses': 60,
                 'wildCardRank': str(i), 'wildCardGamesBack': str(i - 3)}
                for i in range(1, 8)]},
            {'league': {'id': 104}, 'teamRecords': [
                {'team': {'id': 119}, 'wins': 81, 'losses': 59,
                 'wildCardRank': str(i), 'wildCardGamesBack': str(i - 3)}
                for i in range(1, 7)]},
        ]}

    def test_five_teams_per_league(self):
        rows = parse_mlb_wild_card(self.payload)
        self.assertEqual(len(rows), 10)
        self.assertEqual([r.rank for r in rows[:5]], [1, 2, 3, 4, 5])
        self.assertEqual([r.rank for r in rows[5:]], [1, 2, 3, 4, 5])

    def test_uses_official_wild_card_games_back(self):
        rows = parse_mlb_wild_card(self.payload)
        self.assertEqual(rows[3].games_back, '1')

    def test_missing_wild_card_rank_is_excluded(self):
        self.payload['records'][0]['teamRecords'][0].pop('wildCardRank')
        rows = parse_mlb_wild_card(self.payload)
        self.assertNotIn(1, [r.rank for r in rows if r.group == 'AL_WILD_CARD'])

    def test_fetch_requests_wild_card_standings(self):
        urls = []
        def fetch(url):
            urls.append(url)
            return self.payload
        rows = fetch_mlb_wild_card(fetch=fetch)
        self.assertEqual(len(rows), 10)
        self.assertIn('standingsTypes=wildCard', urls[0])

    def test_group_selection(self):
        rows = fetch_mlb_wild_card_group('NL_WILD_CARD',
                                        fetcher=lambda: parse_mlb_wild_card(self.payload))
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r.group == 'NL_WILD_CARD' for r in rows))


if __name__ == '__main__':
    unittest.main()
