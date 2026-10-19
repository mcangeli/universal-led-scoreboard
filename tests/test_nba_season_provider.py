import io
import unittest

from universal_led.nba_season_provider import fetch_nba_season_windows


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class NBASeasonProviderTests(unittest.TestCase):
    def test_fetches_verified_boundaries(self):
        requests = []
        def opener(request, timeout):
            requests.append((request.full_url, timeout))
            return _Response(b'{"seasons":[{"regularSeasonStartDate":"2026-10-20","regularSeasonEndDate":"2027-04-11"}]}')
        windows = fetch_nba_season_windows('NBA', url='https://example.org/nba-seasons',
                                           opener=opener)
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0]['end'], '2027-04-12T00:00:00Z')
        self.assertEqual(requests, [('https://example.org/nba-seasons', 8)])

    def test_requires_explicit_https_source(self):
        for url in ('http://example.org/nba', '', 'file:///tmp/nba.json'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                fetch_nba_season_windows('NBA', url=url, opener=lambda *_args, **_kwargs: None)

    def test_missing_boundaries_fail_closed(self):
        with self.assertRaises(ValueError):
            fetch_nba_season_windows('NBA', url='https://example.org/nba',
                                     opener=lambda *_args, **_kwargs: _Response(b'{"seasons":[]}'))


if __name__ == '__main__':
    unittest.main()
