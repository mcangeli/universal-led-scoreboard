import unittest
from datetime import datetime, timedelta, timezone
from universal_led.season_countdown import SPORTS, SeasonMilestone, countdown
from universal_led.season_countdown_screen import SeasonCountdownScreen

class SeasonCountdownScreenTests(unittest.TestCase):
    def test_all_sports_render_native_64x32(self):
        now = datetime(2026, 10, 15, tzinfo=timezone.utc)
        for sport in SPORTS:
            with self.subTest(sport=sport):
                event = SeasonMilestone(sport, '2027', now + timedelta(days=142, hours=8))
                frame = SeasonCountdownScreen(countdown(event, now)).render()
                self.assertEqual((frame.width, frame.height), (64, 32))
                self.assertTrue(any(pixel != (0, 0, 0) for row in frame.pixels for pixel in row))

    def test_large_day_count(self):
        now = datetime(2026, 10, 15, tzinfo=timezone.utc)
        event = SeasonMilestone('mlb', '2028', now + timedelta(days=365))
        self.assertEqual(SeasonCountdownScreen(countdown(event, now)).render().width, 64)

if __name__ == '__main__':
    unittest.main()
