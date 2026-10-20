"""Lifecycle adapter for saving pending scoring alerts on a bounded cadence."""
import threading
import time

from .scoring_alert_store import ScoringAlertStore


class ScoringAlertPersistence:
    def __init__(self, alerts, path, *, monotonic=time.monotonic, epoch=time.time,
                 interval=5):
        self.alerts = alerts
        self.store = ScoringAlertStore(path)
        self.monotonic = monotonic
        self.epoch = epoch
        self.interval = interval
        self._save_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None

    def restore(self):
        return self.store.restore(self.alerts, monotonic=self.monotonic(),
                                  epoch=self.epoch())

    def save(self):
        # Always acquire queue lock before disk lock, including transition callbacks.
        # This avoids a save/activation lock inversion across worker threads.
        with self.alerts._lock:
            with self._save_lock:
                self.store.save(self.alerts, monotonic=self.monotonic(), epoch=self.epoch())

    def _save_transition(self):
        try:
            self.save()
        except (OSError, RuntimeError):
            # Never interrupt rendering if persistence is unavailable.
            pass

    def start(self):
        if self._thread is not None:
            return
        self.alerts.on_queue_transition = self._save_transition
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name="uls-scoring-alert-persistence")
        self._thread.start()

    def _run(self):
        while not self._stop.wait(self.interval):
            try:
                self.save()
            except (OSError, RuntimeError):
                # Persistence failures must not stop the live scoreboard.
                continue

    def stop(self):
        if self.alerts.on_queue_transition == self._save_transition:
            self.alerts.on_queue_transition = None
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
        try:
            self.save()
        except (OSError, RuntimeError):
            pass
