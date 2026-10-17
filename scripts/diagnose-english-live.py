#!/usr/bin/env python3
"""Read-only English football live-event diagnostic.

Fetches each division's scoreboard and prints whether live clocks and
scoring-event IDs are actually present. Never writes configuration.
"""
import json
import sys
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

# Support direct execution from a source checkout without package installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from universal_led.english_football import COMPETITIONS
from universal_led.soccer_feed import parse_scoreboard
from universal_led.soccer_rotation import is_live

BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"


def inspect(payload, league):
    games = parse_scoreboard(payload, league)
    live = [game for game in games if is_live(game)]
    return {
        "fixtures": len(games),
        "live": len(live),
        "live_clocks": sum(bool(game.clock) for game in live),
        "live_goal_events": sum(len(game.goals) for game in live),
        "live_goal_ids": sum(bool(goal.event_id) for game in live for goal in game.goals),
        "halftime": sum(game.status == "halftime" for game in live),
        "final": sum(game.status in ("post", "final") for game in games),
    }


def probe(day, opener=urlopen):
    results = {}
    for league, slug in COMPETITIONS.items():
        request = Request(f"{BASE}/{slug}/scoreboard?dates={day:%Y%m%d}",
                          headers={"Accept": "application/json",
                                   "User-Agent": "UniversalLEDScoreboard/0.6-diagnostics"})
        try:
            with opener(request, timeout=8) as response:
                results[league] = {"coverage": inspect(json.load(response), league)}
        except (OSError, ValueError, TypeError, KeyError) as exc:
            results[league] = {"error": str(exc)}
    return results


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    try:
        day = date.fromisoformat(args[0]) if args else date.today()
    except ValueError:
        print("Usage: python3 scripts/diagnose-english-live.py [YYYY-MM-DD]", file=sys.stderr)
        return 2
    print(f"English football live data coverage: {day}")
    results = probe(day)
    for league, result in results.items():
        if "error" in result:
            print(f"{league}: ERROR {result['error']}")
        else:
            print(f"{league}: " + " ".join(f"{k}={v}" for k, v in result["coverage"].items()))
    if not any(result.get("coverage", {}).get("live") for result in results.values()):
        print("No live fixtures observed. Live clock and goal-event support remain unverified.")
    else:
        print("Goal events are counted only when explicitly provided by the scoreboard feed.")
    return int(any("error" in result for result in results.values()))


if __name__ == "__main__":
    sys.exit(main())
