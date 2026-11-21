"""Restart unexpectedly stopped background pollers without touching healthy workers."""


def restart_dead_workers(workers):
    """Return names restarted; never start a worker that is intentionally stopped.

    The caller supplies only workers currently enabled by configuration.
    A worker without a thread has not necessarily started yet, so it is not
    restarted here.
    """
    restarted = []
    for name, worker in workers.items():
        thread = getattr(worker, "_thread", None)
        if thread is not None and not thread.is_alive():
            worker.start()
            restarted.append(name)
    return tuple(restarted)
