import unittest
from datetime import datetime, timedelta, timezone
from universal_led.season_countdown import SeasonMilestone, countdown, should_display, SPORTS

class SeasonCountdownTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2027, 3, 1, 12, tzinfo=timezone.utc)
        self.event = SeasonMilestone('mlb', '2027', self.now + timedelta(days=3, hours=2, minutes=15))

    def test_all_sports_supported_by_shared_model(self):
        for sport in SPORTS:
            with self.subTest(sport=sport):
                self.assertEqual(SeasonMilestone(sport, '2027', self.event.starts_at).sport, sport)

    def test_countdown_parts(self):
        result = countdown(self.event, self.now)
        self.assertEqual((result.days, result.hours, result.minutes), (3, 2, 15))

    def test_cross_timezone(self):
        eastern = timezone(timedelta(hours=-4))
        same_instant = self.now.astimezone(eastern)
        self.assertEqual(countdown(self.event, same_instant), countdown(self.event, self.now))

    def test_fractional_second_rounds_up(self):
        event = SeasonMilestone('mlb', '2027', self.now + timedelta(seconds=0.5))
        self.assertEqual(countdown(event, self.now).seconds_remaining, 1)

    def test_expired_event_is_not_shown(self):
        self.assertIsNone(countdown(self.event, self.event.starts_at))
        self.assertIsNone(countdown(self.event, self.event.starts_at + timedelta(seconds=1)))

    def test_naive_datetime_rejected(self):
        with self.assertRaises(ValueError):
            SeasonMilestone('mlb', '2027', datetime(2027, 3, 1))
        with self.assertRaises(ValueError):
            countdown(self.event, datetime(2027, 3, 1))

    def test_favorite_requires_team(self):
        with self.assertRaises(ValueError):
            SeasonMilestone('mlb', '2027', self.event.starts_at, target='favorite')

    def test_live_game_always_wins(self):
        result = countdown(self.event, self.now)
        for window in ('always', 'offseason', 'within_days'):
            self.assertFalse(should_display(result, enabled=True, window=window, live_game=True))

    def test_display_windows(self):
        result = countdown(self.event, self.now)
        self.assertTrue(should_display(result, enabled=True, window='offseason'))
        self.assertFalse(should_display(result, enabled=True, window='offseason', season_active=True))
        self.assertTrue(should_display(result, enabled=True, window='within_days', within_days=4))
        self.assertFalse(should_display(result, enabled=True, window='within_days', within_days=2))
        self.assertTrue(should_display(result, enabled=True, window='always', season_active=True))
        self.assertFalse(should_display(result, enabled=False, window='always'))

if __name__ == '__main__':
    unittest.main()
