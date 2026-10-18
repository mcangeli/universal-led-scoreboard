#!/usr/bin/env python3
"""Read-only ESPN match-summary structure probe; prints counts, not player data."""
import json
import sys
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from universal_led.english_football import COMPETITIONS
from universal_led.english_summary import parse_key_event_goals

BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"


def fetch(url, opener=urlopen):
    req = Request(url, headers={"Accept": "application/json",
                                "User-Agent": "UniversalLEDScoreboard/0.6-diagnostics"})
    with opener(req, timeout=8) as response:
        return json.load(response)


def event_section(value):
    """Summarize the shape of a section without printing player or commentary text."""
    if isinstance(value, list):
        rows = value
        shape = "list"
    elif isinstance(value, dict):
        shape = "object"
        rows = next((value[key] for key in ("events", "items", "plays")
                     if isinstance(value.get(key), list)), [])
    else:
        return {"shape": type(value).__name__, "count": 0, "fields": "",
                "goal_markers": 0}
    fields = sorted({key for row in rows[:20] if isinstance(row, dict) for key in row})
    markers = sum(
        bool(row.get("scoringPlay") or row.get("isGoal") or row.get("goal"))
        or any("goal" in str((row.get(key) or {}).get("text", "")).lower()
               for key in ("type",) if isinstance(row.get(key), dict))
        for row in rows if isinstance(row, dict)
    )
    return {"shape": shape, "count": len(rows), "fields": ",".join(fields),
            "goal_markers": markers}


def summary_coverage(payload):
    if not isinstance(payload, dict):
        raise ValueError("Summary response must be an object")
    keys = tuple(sorted(payload.keys()))
    scoring = payload.get("scoringPlays") or []
    plays = payload.get("plays") or []
    if isinstance(plays, dict):
        plays = plays.get("allPlays") or []
    if not isinstance(scoring, list):
        scoring = []
    if not isinstance(plays, list):
        plays = []
    key_events = event_section(payload.get("keyEvents"))
    parsed_goals = parse_key_event_goals(payload)
    commentary = event_section(payload.get("commentary"))
    return {"keys": ",".join(keys),
            **{"key_events_" + key: value for key, value in key_events.items()},
            **{"commentary_" + key: value for key, value in commentary.items()},
            "parsed_goals": len(parsed_goals),
            "parsed_team_ids": sum(bool(goal.team_id) for goal in parsed_goals),
            "parsed_scorers": sum(bool(goal.scorer) for goal in parsed_goals),
            "parsed_minutes": sum(bool(goal.minute) for goal in parsed_goals),
            "parsed_unique_ids": len({goal.event_id for goal in parsed_goals}),
            "scoring_plays": len(scoring),
            "plays": len(plays),
            "play_scoring_flags": sum(bool(p.get("scoringPlay")) for p in plays if isinstance(p, dict))}


def probe(day, opener=urlopen):
    results = {}
    for league, slug in COMPETITIONS.items():
        try:
            board = fetch(f"{BASE}/{slug}/scoreboard?dates={day:%Y%m%d}", opener)
            events = board.get("events") or []
            if not events:
                results[league] = {"status": "no fixtures"}
                continue
            event_id = str(events[0].get("id", ""))
            if not event_id.isdigit():
                raise ValueError("Missing numeric match ID")
            summary = fetch(f"{BASE}/{slug}/summary?event={event_id}", opener)
            results[league] = {"event_id": event_id, **summary_coverage(summary)}
        except (OSError, ValueError, TypeError, KeyError) as exc:
            results[league] = {"error": str(exc)}
    return results


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    try:
        day = date.fromisoformat(args[0]) if args else date.today()
    except ValueError:
        print("Usage: python3 scripts/probe-english-summary.py [YYYY-MM-DD]", file=sys.stderr)
        return 2
    print(f"ESPN English football summary coverage: {day}")
    results = probe(day)
    for league, data in results.items():
        print(f"{league}: " + " ".join(f"{k}={v}" for k, v in data.items()))
    print("One fixture sampled per division; summary fields are observational, not guaranteed.")
    return int(any("error" in result for result in results.values()))


if __name__ == "__main__":
    sys.exit(main())
