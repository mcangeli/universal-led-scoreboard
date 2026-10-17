#!/usr/bin/env python3
"""Read-only English football field coverage probe. No API keys or writes."""
import json
import sys
from datetime import date
from urllib.request import Request, urlopen

LEAGUES = {"EPL": "eng.1", "CHAMPIONSHIP": "eng.2",
           "LEAGUE_ONE": "eng.3", "LEAGUE_TWO": "eng.4"}
BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"


def coverage(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("Missing events array")
    counts = dict(matches=0, kickoff=0, team_ids=0, team_names=0,
                  status=0, scores=0, live=0, live_clock=0, scoring_events=0)
    for event in payload["events"]:
        if not isinstance(event, dict) or not event.get("id"):
            raise ValueError("Missing event ID")
        competitions = event.get("competitions") or []
        if not competitions or not isinstance(competitions[0], dict):
            raise ValueError("Missing competition")
        comp = competitions[0]
        teams = {x.get("homeAway"): x for x in comp.get("competitors") or []
                 if isinstance(x, dict)}
        if "home" not in teams or "away" not in teams:
            raise ValueError("Missing home or away team")
        home, away = teams["home"], teams["away"]
        ht, at = home.get("team") or {}, away.get("team") or {}
        status = event.get("status") or comp.get("status") or {}
        state = (status.get("type") or {}).get("state")
        counts["matches"] += 1
        counts["kickoff"] += bool(event.get("date") or comp.get("date"))
        counts["team_ids"] += bool(ht.get("id") and at.get("id"))
        counts["team_names"] += bool(
            (ht.get("displayName") or ht.get("name")) and
            (at.get("displayName") or at.get("name")))
        counts["status"] += bool(state)
        counts["scores"] += (home.get("score") is not None and
                             away.get("score") is not None)
        if state in ("in", "live", "in_progress"):
            counts["live"] += 1
            counts["live_clock"] += bool(status.get("displayClock") or status.get("clock"))
        counts["scoring_events"] += sum(
            bool(x.get("id")) for x in comp.get("details") or []
            if isinstance(x, dict) and x.get("scoringPlay"))
    return counts


def probe(day, opener=urlopen):
    results = []
    for name, slug in LEAGUES.items():
        req = Request(f"{BASE}/{slug}/scoreboard?dates={day:%Y%m%d}",
                      headers={"Accept": "application/json",
                               "User-Agent": "UniversalLEDScoreboard/0.6-validation"})
        try:
            with opener(req, timeout=8) as response:
                results.append((name, coverage(json.load(response)), None))
        except Exception as exc:
            results.append((name, None, str(exc)))
    return results


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        day = date.fromisoformat(argv[0]) if argv else date.today()
    except ValueError:
        print("Usage: python3 scripts/probe-english-contract.py [YYYY-MM-DD]", file=sys.stderr)
        return 2
    print(f"English football ESPN field coverage: {day.isoformat()}")
    rows = probe(day)
    for name, fields, error in rows:
        if error:
            print(f"{name:13} ERROR {error}")
        else:
            print(f"{name:13} " + " ".join(f"{key}={value}" for key, value in fields.items()))
    print("Field counts are observations, not guarantees; live=0 cannot validate live events.")
    return int(any(error for _, _, error in rows))


if __name__ == "__main__":
    sys.exit(main())
