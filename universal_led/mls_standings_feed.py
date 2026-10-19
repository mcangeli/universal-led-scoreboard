"""MLS conference standings using the existing league-neutral standings model."""
import json
from urllib.request import Request, urlopen
from .standings import Standing

MLS_STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/soccer/usa.1/standings"
MLS_CONFERENCES = ("Eastern Conference", "Western Conference")


def parse_mls_standings(payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid MLS standings response")
    rows = []
    for conference in payload.get("children") or []:
        name = conference.get("name", "")
        if name not in MLS_CONFERENCES:
            continue
        entries = (conference.get("standings") or {}).get("entries") or []
        for index, entry in enumerate(entries, 1):
            team = entry.get("team") or {}
            stats = {stat.get("name"): stat.get("value")
                     for stat in entry.get("stats", [])}
            try:
                wins, losses = int(stats["wins"]), int(stats["losses"])
                draws = int(stats.get("ties", stats.get("draws", 0)))
                played = int(stats.get("gamesPlayed", wins + losses + draws))
                points = int(stats["points"])
                rank = int(stats.get("rank", index))
                difference = int(stats.get("pointDifferential",
                                           stats.get("goalDifference", 0)))
                rows.append(Standing(
                    league="MLS", group=name, team_id=str(team["id"]),
                    abbreviation=team.get("abbreviation") or None,
                    played=played, wins=wins, losses=losses, draws=draws,
                    points=points, goal_difference=difference, rank=rank))
            except (KeyError, ValueError, TypeError):
                continue
    return tuple(rows)


def fetch_mls_standings(_league="MLS", *, opener=None, timeout=12):
    request = Request(MLS_STANDINGS_URL, headers={
        "User-Agent": "UniversalLEDScoreboard/0.7",
        "Accept": "application/json",
    })
    with (opener or urlopen)(request, timeout=timeout) as response:
        return parse_mls_standings(json.load(response))
