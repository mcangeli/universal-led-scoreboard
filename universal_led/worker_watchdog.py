"""Restart unexpectedly stopped background pollers without touching healthy workers."""
import logging

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
