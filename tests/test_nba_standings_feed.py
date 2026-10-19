import unittest
from universal_led.nba_standings_feed import parse_nba_standings, fetch_nba_conference


def row(code, wins, losses, rank):
    return {'team': {'abbreviation': code}, 'stats': [
        {'name': 'wins', 'value': wins}, {'name': 'losses', 'value': losses},
        {'name': 'playoffSeed', 'value': rank},
        {'name': 'gamesBehind', 'displayValue': '2.5'}]}


class NBAStandingsFeedTests(unittest.TestCase):
    def test_conferences_and_official_ranks(self):
        payload = {'children': [
            {'name': 'Eastern Conference', 'standings': {'entries': [
                row('BOS', 40, 10, 1), row('ATL', 30, 20, 5)]}},
            {'name': 'Western Conference', 'standings': {'entries': [
                row('DEN', 38, 12, 2)]}}]}
        rows = parse_nba_standings(payload)
        self.assertEqual([r.group for r in rows], ['Eastern', 'Eastern', 'Western'])
        self.assertEqual(rows[1].rank, 5)
        self.assertEqual(rows[1].games_back, '2.5')
        self.assertEqual(rows[0].played, 50)
        self.assertEqual([r.team_id for r in fetch_nba_conference('Western', fetcher=lambda _: rows)], ['DEN'])

    def test_missing_provider_data_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_nba_standings({'children': []})

    def test_unknown_conference_rejected(self):
        with self.assertRaises(ValueError):
            fetch_nba_conference('Central', fetcher=lambda _: ())


if __name__ == '__main__':
    unittest.main()
