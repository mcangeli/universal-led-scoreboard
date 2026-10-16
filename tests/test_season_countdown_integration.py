import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from universal_led.config_store import save_config
from universal_led.screen_rotation import choose_screen
from universal_led.season_countdown_settings import DEFAULT, current, load

class CountdownIntegrationTests(unittest.TestCase):
    def test_legacy_rotation_unchanged(self):
        self.assertEqual([choose_screen(i, has_game=True, clock=True, weather=True, news=True)
                          for i in range(4)], ['clock', 'weather', 'news', 'game'])

    def test_optional_slot(self):
        self.assertEqual([choose_screen(i, has_game=False, clock=True, weather=False,
                                        news=False, countdown=True) for i in range(4)],
                         ['clock', 'countdown', 'clock', 'countdown'])

    def test_disabled_by_default(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(load(folder), DEFAULT)
            self.assertIsNone(current(folder))

    def test_manual_override_and_expiry(self):
        with tempfile.TemporaryDirectory() as folder:
            now = datetime(2026, 10, 15, tzinfo=timezone.utc)
            settings = dict(DEFAULT, enabled=True, season='2027',
                            opening_at=(now + timedelta(days=10)).isoformat())
            save_config(folder, 'season_countdown', settings)
            self.assertEqual(current(folder, now=now).days, 10)
            self.assertIsNone(current(folder, now=now, season_active=True))
            self.assertIsNone(current(folder, now=now, live_game=True))
            self.assertIsNone(current(folder, now=now + timedelta(days=11)))

    def test_reject_naive_opening_time(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                save_config(folder, 'season_countdown',
                            dict(DEFAULT, enabled=True, season='2027',
                                 opening_at='2027-03-01T12:00:00'))

if __name__ == '__main__':
    unittest.main()
