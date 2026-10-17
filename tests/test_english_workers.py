"""English worker lifecycle tests without networking or background threads."""
import unittest
from types import SimpleNamespace
from universal_led.english_workers import sync_english_workers


class FakeWorker:
    def __init__(self):
        self.feed = SimpleNamespace(refresh_seconds=60)
        self.running = False
        self.started = 0
        self.stopped = 0
        self.timezone = None

    def start(self):
        self.running = True
        self.started += 1

    def stop(self):
        self.running = False
        self.stopped += 1

    def set_timezone(self, value):
        self.timezone = value


class EnglishWorkerLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.workers = {name: FakeWorker() for name in
                        ("EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO")}

    def sync(self, enabled, leagues):
        sync_english_workers(self.workers, sport_enabled=enabled,
                             enabled_leagues=leagues, refresh_seconds=90,
                             timezone_name="America/New_York")

    def test_only_selected_divisions_start(self):
        self.sync(True, ["EPL", "LEAGUE_TWO"])
        self.assertEqual({key for key, worker in self.workers.items() if worker.running},
                         {"EPL", "LEAGUE_TWO"})
        self.assertTrue(all(worker.feed.refresh_seconds == 90 for worker in self.workers.values()))

    def test_deselected_division_stops(self):
        self.sync(True, ["EPL", "CHAMPIONSHIP"])
        self.sync(True, ["CHAMPIONSHIP"])
        self.assertFalse(self.workers["EPL"].running)
        self.assertTrue(self.workers["CHAMPIONSHIP"].running)

    def test_disabling_sport_stops_all_workers(self):
        self.sync(True, ["EPL", "LEAGUE_ONE"])
        self.sync(False, ["EPL", "LEAGUE_ONE"])
        self.assertFalse(any(worker.running for worker in self.workers.values()))

    def test_invalid_division_is_rejected_before_changes(self):
        with self.assertRaises(ValueError):
            self.sync(True, ["INVALID"])
        self.assertFalse(any(worker.started for worker in self.workers.values()))


if __name__ == "__main__":
    unittest.main()
