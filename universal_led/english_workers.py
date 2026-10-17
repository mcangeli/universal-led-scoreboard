"""Keep English division polling aligned with the current saved settings.

Only selected divisions poll. Disabling the sport stops every English worker.
"""
from .english_football import COMPETITIONS


def sync_english_workers(workers, *, sport_enabled, enabled_leagues,
                         refresh_seconds, timezone_name):
    selected = set(enabled_leagues)
    if not selected <= COMPETITIONS.keys():
        raise ValueError("Unknown English division")
    # Stop deselected workers before starting any newly selected feeds.
    # Avoid repeatedly stopping idle workers or starting running workers.
    for league, worker in workers.items():
        should_run = bool(sport_enabled and league in selected)
        running = worker._thread is not None if hasattr(worker, '_thread') else getattr(worker, 'running', False)
        if running and not should_run:
            worker.stop()
    for league, worker in workers.items():
        worker.feed.refresh_seconds = refresh_seconds
        worker.set_timezone(timezone_name)
        should_run = bool(sport_enabled and league in selected)
        running = worker._thread is not None if hasattr(worker, '_thread') else getattr(worker, 'running', False)
        if should_run and not running:
            worker.start()
