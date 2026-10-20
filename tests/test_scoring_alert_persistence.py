"""Lifecycle persistence integration tests."""
import tempfile
import unittest
from pathlib import Path
from universal_led.scoring_alerts import ScoringAlerts, ScoreEvent
from universal_led.scoring_alert_persistence import ScoringAlertPersistence


class ScoringPersistenceTests(unittest.TestCase):
    def test_lifecycle_save_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "alerts.json"
            source = ScoringAlerts(enabled=True, scope="all")
            source.set_clock(lambda: 100.)
            source.baseline("nhl", "NHL", "1", ())
            source.observe("nhl", "NHL", "1",
                           [ScoreEvent("nhl", "NHL", "1", "goal", "BOS", "GOAL")])
            writer = ScoringAlertPersistence(source, path, monotonic=lambda: 100.,
                                             epoch=lambda: 1000.)
            writer.save()
            restored = ScoringAlerts(enabled=True, scope="all")
            restored.set_clock(lambda: 110.)
            reader = ScoringAlertPersistence(restored, path, monotonic=lambda: 110.,
                                             epoch=lambda: 1010.)
            self.assertEqual(reader.restore(), 1)
            self.assertEqual(restored.next_alert(110).event_id, "goal")

    def test_disabled_settings_prevent_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "alerts.json"
            source = ScoringAlerts(enabled=True, scope="all")
            source.set_clock(lambda: 100.)
            source.baseline("nhl", "NHL", "1", ())
            source.observe("nhl", "NHL", "1",
                           [ScoreEvent("nhl", "NHL", "1", "goal", "BOS", "GOAL")])
            ScoringAlertPersistence(source, path, monotonic=lambda: 100.,
                                    epoch=lambda: 1000.).save()
            disabled = ScoringAlerts()
            self.assertEqual(ScoringAlertPersistence(
                disabled, path, monotonic=lambda: 110.,
                epoch=lambda: 1010.).restore(), 0)


if __name__ == "__main__":
    unittest.main()
