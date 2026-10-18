#!/usr/bin/env python3
"""Read-only ESPN English football endpoint probe. No credentials or config changes."""
import json
import sys
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

LEAGUES = {
    "EPL": "eng.1",
    "CHAMPIONSHIP": "eng.2",
    "LEAGUE_ONE": "eng.3",
    "LEAGUE_TWO": "eng.4",
}
BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"


def inspect_payload(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("missing events array")
    events = payload["events"]
    if not events:
        return "EMPTY", 0, 0
    valid = 0
    for event in events:
        if not isinstance(event, dict) or not event.get("id"):
            continue
        competitions = event.get("competitions") or []
        if not competitions or not isinstance(competitions[0], dict):
            continue
        competitors = competitions[0].get("competitors") or []
        sides = {row.get("homeAway") for row in competitors if isinstance(row, dict)}
        if not {"home", "away"} <= sides:
            continue
        valid += 1
    if valid != len(events):
        raise ValueError(f"{len(events) - valid} events missing identity/home-away fields")
    return "OK", len(events), valid


def probe(day, opener=urlopen):
    results = []
    for name, slug in LEAGUES.items():
        url = f"{BASE}/{slug}/scoreboard?dates={day:%Y%m%d}"
        request = Request(url, headers={"Accept": "application/json",
                                        "User-Agent": "UniversalLEDScoreboard/0.6-validation"})
        try:
            with opener(request, timeout=8) as response:
                payload = json.load(response)
            status, count, valid = inspect_payload(payload)
            results.append((name, slug, status, count, valid))
        except (HTTPError, URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError) as exc:
            results.append((name, slug, "ERROR", 0, str(exc)))
    return results


def main():
    try:
        day = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    except ValueError:
        print("Usage: python3 scripts/probe-english-football.py [YYYY-MM-DD]", file=sys.stderr)
        return 2
    print(f"ESPN English football endpoint check: {day.isoformat()}")
    results = probe(day)
    for name, slug, status, count, detail in results:
        print(f"{name:13} {slug:6} {status:5} events={count} detail={detail}")
    print("EMPTY means valid JSON with no games for this date; it does NOT prove season coverage.")
    return 1 if any(row[2] == "ERROR" for row in results) else 0


if __name__ == "__main__":
    sys.exit(main())
