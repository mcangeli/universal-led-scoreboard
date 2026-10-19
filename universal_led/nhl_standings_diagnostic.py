"""Read-only NHL standings diagnostic; run with python -m universal_led.nhl_standings_diagnostic."""
from datetime import datetime, timezone
import json

from .nhl_season_calendar import fetch_nhl_season_windows
from .nhl_standings_feed import fetch_nhl_standings
from .standings_season_calendar import parse_season_windows, season_phase


def diagnose(*, season_fetcher=fetch_nhl_season_windows, standings_fetcher=fetch_nhl_standings):
    result = {"sport": "NHL", "season_phase": "unknown", "season_error": None,
              "standings_rows": 0, "standings_error": None, "groups": {}}
    try:
        windows = parse_season_windows(season_fetcher("NHL"))
        result["season_phase"] = season_phase(windows, datetime.now(timezone.utc))
    except Exception as exc:
        result["season_error"] = str(exc)
    try:
        rows = tuple(standings_fetcher("NHL"))
        result["standings_rows"] = len(rows)
        for row in rows:
            result["groups"][row.group] = result["groups"].get(row.group, 0) + 1
    except Exception as exc:
        result["standings_error"] = str(exc)
    result["eligible"] = result["season_phase"] == "regular" and result["standings_rows"] > 0
    return result


def main():
    print(json.dumps(diagnose(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
