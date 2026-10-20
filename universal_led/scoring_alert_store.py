"""Atomic on-disk snapshots for pending scoring alerts.

Storage is deliberately independent of the renderer and service lifecycle.
Only the pending queue is persisted; active alerts are never replayed.
"""
import json
import os
from pathlib import Path
import tempfile
import time


class ScoringAlertStore:
    def __init__(self, path):
        self.path = Path(path)

    def save(self, alerts, *, monotonic=None, epoch=None):
        monotonic = time.monotonic() if monotonic is None else monotonic
        epoch = time.time() if epoch is None else epoch
        snapshot = alerts.export_pending(now_monotonic=monotonic, now_epoch=epoch)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".scoring-alerts-", suffix=".tmp",
                                         dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(snapshot, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def restore(self, alerts, *, monotonic=None, epoch=None):
        monotonic = time.monotonic() if monotonic is None else monotonic
        epoch = time.time() if epoch is None else epoch
        try:
            with self.path.open("r", encoding="utf-8") as stream:
                snapshot = json.load(stream)
        except (OSError, ValueError):
            return 0
        return alerts.import_pending(snapshot, now_monotonic=monotonic,
                                     now_epoch=epoch)
