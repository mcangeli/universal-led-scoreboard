"""Keep English division polling aligned with the current saved settings.

Only selected divisions poll. Disabling the sport stops every English worker.
"""
from .english_football import COMPETITIONS


def sync_english_workers(workers, *, sport_enabled, enabled_leagues,
                         refresh_seconds, timezone_name):
    selected = set(enabled_leagues)
    if not selected <= COMPETITIONS.keys():
        raise ValueError("Unknown English division")
    for league, worker in workers.items():
        worker.feed.refresh_seconds = refresh_seconds
        worker.set_timezone(timezone_name)
        if sport_enabled and league in selected:
            worker.start()
        else:
            worker.stop()
