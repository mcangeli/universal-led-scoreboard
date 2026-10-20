"""Lifecycle persistence integration tests."""
import tempfile
import threading
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

    def test_activation_immediately_removes_alert_from_disk(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "alerts.json"
            source = ScoringAlerts(enabled=True, scope="all")
            source.set_clock(lambda: 100.)
            source.baseline("nhl", "NHL", "1", ())
            goal = ScoreEvent("nhl", "NHL", "1", "goal", "BOS", "GOAL")
            source.observe("nhl", "NHL", "1", [goal])
            writer = ScoringAlertPersistence(source, path, monotonic=lambda: 100.,
                                             epoch=lambda: 1000., interval=3600)
            writer.save()
            writer.start()
            try:
                self.assertEqual(source.next_alert(100), goal)
                recovered = ScoringAlerts(enabled=True, scope="all")
                self.assertEqual(ScoringAlertPersistence(
                    recovered, path, monotonic=lambda: 101.,
                    epoch=lambda: 1001.).restore(), 0)
            finally:
                writer.stop()

    def test_failed_render_requeues_and_checkpoints(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "alerts.json"
            source = ScoringAlerts(enabled=True, scope="all")
            source.set_clock(lambda: 100.)
            source.baseline("nhl", "NHL", "1", ())
            goal = ScoreEvent("nhl", "NHL", "1", "goal", "BOS", "GOAL")
            source.observe("nhl", "NHL", "1", [goal])
            writer = ScoringAlertPersistence(source, path, monotonic=lambda: 100.,
                                             epoch=lambda: 1000., interval=3600)
            writer.start()
            try:
                self.assertEqual(source.next_alert(100), goal)
                source.render_failed(goal)
                recovered = ScoringAlerts(enabled=True, scope="all")
                self.assertEqual(ScoringAlertPersistence(
                    recovered, path, monotonic=lambda: 101.,
                    epoch=lambda: 1001.).restore(), 1)
            finally:
                writer.stop()

    def test_concurrent_saves_and_activation_do_not_deadlock(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "alerts.json"
            alerts = ScoringAlerts(enabled=True, scope="all")
            alerts.set_clock(lambda: 100.)
            alerts.baseline("nhl", "NHL", "1", ())
            goal = ScoreEvent("nhl", "NHL", "1", "goal", "BOS", "GOAL")
            alerts.observe("nhl", "NHL", "1", [goal])
            writer = ScoringAlertPersistence(alerts, path, monotonic=lambda: 100.,
                                             epoch=lambda: 1000., interval=3600)
            writer.start()
            errors = []
            def save_many():
                try:
                    for _ in range(30):
                        writer.save()
                except Exception as exc:
                    errors.append(exc)
            thread = threading.Thread(target=save_many, daemon=True)
            try:
                thread.start()
                self.assertEqual(alerts.next_alert(100), goal)
                thread.join(timeout=3)
                self.assertFalse(thread.is_alive(), "Concurrent checkpoint deadlocked")
                self.assertEqual(errors, [])
                restored = ScoringAlerts(enabled=True, scope="all")
                self.assertEqual(ScoringAlertPersistence(
                    restored, path, monotonic=lambda: 101.,
                    epoch=lambda: 1001.).restore(), 0)
            finally:
                writer.stop()

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
