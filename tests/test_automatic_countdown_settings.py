import tempfile
import unittest
from datetime import datetime, timezone
from universal_led.config_store import save_config
from universal_led.season_countdown_settings import DEFAULT, current, load

class AutomaticCountdownSettingsTests(unittest.TestCase):
    def test_old_manual_settings_load(self):
        with tempfile.TemporaryDirectory() as folder:
            old = {key: value for key, value in DEFAULT.items() if key != 'source'}
            save_config(folder, 'season_countdown', old)
            self.assertEqual(load(folder)['source'], 'manual')

    def test_automatic_provider(self):
        class Provider:
            def opening(self, season, *, target, team):
                from universal_led.season_countdown import SeasonMilestone
                return SeasonMilestone('mlb', season, datetime(2027, 3, 26, tzinfo=timezone.utc))
        with tempfile.TemporaryDirectory() as folder:
            save_config(folder, 'season_countdown', dict(DEFAULT, enabled=True, source='automatic',
                season='2027', opening_at=None))
            now = datetime(2026, 10, 16, tzinfo=timezone.utc)
            self.assertIsNotNone(current(folder, now=now, provider=Provider()))
            self.assertIsNone(current(folder, now=now))

    def test_no_schedule_is_not_guessed(self):
        class Provider:
            def opening(self, season, *, target, team):
                return None
        with tempfile.TemporaryDirectory() as folder:
            save_config(folder, 'season_countdown', dict(DEFAULT, enabled=True, source='automatic',
                season='2027'))
            self.assertIsNone(current(folder, provider=Provider()))

    def test_other_sports_cannot_use_mlb_auto_source(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                save_config(folder, 'season_countdown', dict(DEFAULT, enabled=True,
                    source='automatic', sport='nhl', season='2027'))

if __name__ == '__main__':
    unittest.main()
