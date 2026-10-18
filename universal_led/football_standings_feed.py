"""Fetch and normalize official ESPN football standings outside frame rendering."""
import json
from urllib.request import Request, urlopen

from .english_football import COMPETITIONS
from .standings import Standing, order_standings

BASE = "https://site.api.espn.com/apis/v2/sports/soccer"


def parse_football_standings(payload, league):
    """Read ESPN standings entries, retaining the provider's official order."""
    if league not in COMPETITIONS:
        raise ValueError("Unsupported English competition")
    groups = payload.get("children") or [payload]
    results = []
    for group in groups:
        entries = group.get("standings", {}).get("entries", [])
        if not entries:
            continue
        name = group.get("name") or league
        for index, entry in enumerate(entries, 1):
            stats = {s.get("name"): s.get("value") for s in entry.get("stats", [])}
            def number(*keys, default=0):
                for key in keys:
                    if stats.get(key) is not None:
                        return int(stats[key])
                return default
            team = entry.get("team") or {}
            identifier = str(team.get("id") or "").strip()
            if not identifier:
                continue
            results.append(Standing(
                league=league, group=name, team_id=identifier,
                played=number("gamesPlayed", "games"),
                wins=number("wins"), losses=number("losses"),
                draws=number("ties", "draws"),
                points=number("points", default=0),
                goal_difference=number("pointDifferential", "goalDifference"),
                rank=number("rank", default=index)))
    return tuple(results)


def fetch_football_standings(league, *, timeout=5.0):
    if league not in COMPETITIONS:
        raise ValueError("Unsupported English competition")
    if type(timeout) not in (int, float) or not 0 < timeout <= 30:
        raise ValueError("Invalid timeout")
    url = f"{BASE}/{COMPETITIONS[league]}/standings"
    request = Request(url, headers={"User-Agent": "UniversalLEDScoreboard/0.7",
                                    "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return parse_football_standings(json.load(response), league)
