"""Restart unexpectedly stopped background pollers without touching healthy workers."""
import logging
import time

_LOG = logging.getLogger(__name__)


def restart_dead_workers(workers):
    """Return restarted names; isolate failures so other workers still recover.

    Callers supply only enabled workers. A missing thread means the worker
    has not started and must not be started by the watchdog.
    """
    restarted = []
    for name, worker in workers.items():
        try:
            thread = getattr(worker, "_thread", None)
            if thread is not None and not thread.is_alive():
                worker.start()
                restarted.append(name)
        except Exception:
            _LOG.exception("Could not recover background worker %s", name)
    return tuple(restarted)

def stalled_workers(workers, *, now=None):
    """Identify live workers whose polling attempt has not completed.

    This is diagnostic only. Restarting a blocked live thread can create
    concurrent provider requests and duplicate score notifications.
    """
    now = time.monotonic() if now is None else now
    stalled = []
    for name, worker in workers.items():
        try:
            thread = getattr(worker, "_thread", None)
            started = getattr(worker, "_poll_started", None)
            if thread is None or not thread.is_alive() or started is None:
                continue
            interval = worker.feed.refresh_seconds
            if now - started > max(3 * interval, 180):
                stalled.append(name)
        except Exception:
            _LOG.exception("Could not inspect background worker %s", name)
    return tuple(stalled)
