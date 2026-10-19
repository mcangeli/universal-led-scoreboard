"""NWSL single-table standings adapter for the shared standings model."""
import json
from urllib.request import Request, urlopen

from .standings import Standing

NWSL_STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/soccer/usa.nwsl/standings"
NWSL_GROUP = "NWSL"


def parse_nwsl_standings(payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid NWSL standings response")
    groups = payload.get("children") or [payload]
    rows = []
    for group in groups:
        entries = (group.get("standings") or {}).get("entries") or []
        for index, entry in enumerate(entries, 1):
            team = entry.get("team") or {}
            stats = {item.get("name"): item.get("value") for item in entry.get("stats") or []}
            try:
                identifier = str(team["id"])
                wins = int(stats["wins"])
                losses = int(stats["losses"])
                draws = int(stats.get("ties", stats.get("draws", 0)))
                rows.append(Standing(
                    league="NWSL", group=NWSL_GROUP, team_id=identifier,
                    abbreviation=team.get("abbreviation") or None,
                    played=int(stats.get("gamesPlayed", wins + losses + draws)),
                    wins=wins, losses=losses, draws=draws,
                    points=int(stats["points"]),
                    goal_difference=int(stats.get("pointDifferential", stats.get("goalDifference", 0))),
                    rank=int(stats.get("rank", index))))
            except (KeyError, TypeError, ValueError):
                continue
    if not rows:
        raise ValueError("NWSL standings response contained no usable entries")
    return tuple(rows)


def fetch_nwsl_standings(_league="NWSL", *, opener=None, timeout=12):
    request = Request(NWSL_STANDINGS_URL, headers={
        "User-Agent": "UniversalLEDScoreboard/0.7",
        "Accept": "application/json",
    })
    with (opener or urlopen)(request, timeout=timeout) as response:
        return parse_nwsl_standings(json.load(response))
