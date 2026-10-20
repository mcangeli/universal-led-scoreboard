"""Disk persistence regression tests for the scoring alert queue."""
import json
import tempfile
import unittest
from pathlib import Path

from universal_led.scoring_alerts import ScoreEvent, ScoringAlerts
from universal_led.scoring_alert_store import ScoringAlertStore


def goal(identifier):
    return ScoreEvent("nhl", "NHL", "42", identifier, "BOS", "GOAL")


class ScoringAlertStoreTests(unittest.TestCase):
    def make_alerts(self):
        alerts = ScoringAlerts(enabled=True, scope="all")
        alerts.set_clock(lambda: 100.)
        alerts.baseline("nhl", "NHL", "42", ())
        alerts.observe("nhl", "NHL", "42", [goal("one")])
        return alerts

    def test_save_restore_recent_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ScoringAlertStore(Path(directory) / "nested" / "alerts.json")
            store.save(self.make_alerts(), monotonic=110, epoch=1000)
            restored = ScoringAlerts(enabled=True, scope="all")
            restored.set_clock(lambda: 120.)
            self.assertEqual(store.restore(restored, monotonic=120, epoch=1010), 1)
            self.assertEqual(restored.next_alert(120), goal("one"))

    def test_stale_snapshot_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ScoringAlertStore(Path(directory) / "alerts.json")
            store.save(self.make_alerts(), monotonic=100, epoch=1000)
            restored = ScoringAlerts(enabled=True, scope="all")
            self.assertEqual(store.restore(restored, monotonic=400, epoch=1181), 0)

    def test_missing_or_corrupt_snapshot_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "alerts.json"
            store = ScoringAlertStore(path)
            self.assertEqual(store.restore(ScoringAlerts(enabled=True)), 0)
            path.write_text("{broken", encoding="utf-8")
            self.assertEqual(store.restore(ScoringAlerts(enabled=True)), 0)

    def test_active_alert_not_saved(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ScoringAlertStore(Path(directory) / "alerts.json")
            alerts = self.make_alerts()
            alerts.next_alert(100)
            store.save(alerts, monotonic=100, epoch=1000)
            self.assertEqual(json.loads(store.path.read_text())["pending"], [])


if __name__ == "__main__":
    unittest.main()
