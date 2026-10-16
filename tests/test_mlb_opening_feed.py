import unittest
import time
import threading
from universal_led.mlb_opening_feed import MLBOpeningDayFeed

PAYLOAD = {'dates': [{'games': [
    {'gameType': 'S', 'gameDate': '2027-02-15T18:00:00Z', 'teams': {}},
    {'gameType': 'R', 'gameDate': '2027-03-25T17:00:00Z',
     'teams': {'away': {'team': {'id': 119}}, 'home': {'team': {'id': 147}}}},
    {'gameType': 'R', 'gameDate': '2027-03-26T18:00:00Z',
     'teams': {'away': {'team': {'id': 144}}, 'home': {'team': {'id': 114}}}},
]}]}

class OpeningFeedTests(unittest.TestCase):
    def await_refresh(self, feed, year=2027):
        for _ in range(200):
            if not feed.status(year)['refreshing']:
                return
            time.sleep(0.01)
        self.fail('Opening feed refresh did not complete')

    def test_caches_across_league_and_team_targets(self):
        calls = []
        now = [100]
        def fetch(year):
            calls.append(year)
            return PAYLOAD
        feed = MLBOpeningDayFeed(fetch=fetch, clock=lambda: now[0])
        self.assertIsNone(feed.opening(2027))
        self.await_refresh(feed)
        self.assertEqual(feed.opening(2027).starts_at.day, 25)
        self.assertEqual(feed.opening(2027, target='favorite', team='ATL').starts_at.day, 26)
        self.assertTrue(feed.status(2027)['last_success'])
        self.assertTrue(feed.status(2027)['available'])
        self.assertEqual(calls, [2027])
        now[0] += 21600
        feed.opening(2027)
        self.await_refresh(feed)
        self.assertEqual(calls, [2027, 2027])

    def test_failure_retains_previous_schedule(self):
        calls = [0]
        def fetch(year):
            calls[0] += 1
            if calls[0] > 1:
                raise OSError('offline')
            return PAYLOAD
        now = [100]
        feed = MLBOpeningDayFeed(fetch=fetch, clock=lambda: now[0])
        self.assertIsNone(feed.opening(2027))
        self.await_refresh(feed)
        expected = feed.opening(2027)
        now[0] += 21600
        self.assertEqual(feed.opening(2027), expected)
        self.await_refresh(feed)
        self.assertEqual(feed.last_error, 'offline')
        self.assertTrue(feed.status(2027)['available'])
        self.assertTrue(feed.status(2027)['last_success'])

    def test_initial_failure_is_unavailable(self):
        feed = MLBOpeningDayFeed(fetch=lambda year: (_ for _ in ()).throw(OSError('offline')))
        self.assertIsNone(feed.opening(2027))

    def test_unexpected_fetch_failure_is_contained(self):
        feed = MLBOpeningDayFeed(fetch=lambda year: (_ for _ in ()).throw(RuntimeError('unexpected')))
        self.assertIsNone(feed.opening(2027))
        self.await_refresh(feed)
        self.assertEqual(feed.status(2027)['error'], 'unexpected')
        self.assertFalse(feed.status(2027)['available'])

    def test_slow_network_never_blocks_frame(self):
        release = threading.Event()
        entered = threading.Event()
        def fetch(year):
            entered.set()
            release.wait(2)
            return PAYLOAD
        feed = MLBOpeningDayFeed(fetch=fetch)
        try:
            started = time.monotonic()
            self.assertIsNone(feed.opening(2027))
            self.assertLess(time.monotonic() - started, 0.5)
            self.assertTrue(entered.wait(1))
            started = time.monotonic()
            self.assertIsNone(feed.opening(2027))
            self.assertLess(time.monotonic() - started, 0.5)
        finally:
            release.set()
        self.await_refresh(feed)
        self.assertIsNotNone(feed.opening(2027))

    def test_bad_arguments(self):
        feed = MLBOpeningDayFeed(fetch=lambda year: PAYLOAD)
        with self.assertRaises(ValueError):
            feed.opening(2027, target='favorite')
        with self.assertRaises(ValueError):
            feed.opening(2027, target='other')

if __name__ == '__main__':
    unittest.main()
