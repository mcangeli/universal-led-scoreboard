"""WNBA standings feed for the shared standings model."""
import json
from urllib.request import Request, urlopen

from .standings import Standing

URL = "https://site.api.espn.com/apis/v2/sports/basketball/wnba/standings"


def parse_wnba_standings(payload):
    if not isinstance(payload, dict):
        raise ValueError("Invalid WNBA standings response")
    result = []
    for group in payload.get("children") or [payload]:
        entries = (group.get("standings") or {}).get("entries") or []
        for position, entry in enumerate(entries, 1):
            team = entry.get("team") or {}
            stats = {stat.get("name"): stat.get("value") for stat in entry.get("stats") or []}
            try:
                wins = int(stats["wins"])
                losses = int(stats["losses"])
                result.append(Standing(
                    league="WNBA", group="WNBA", team_id=str(team["id"]),
                    abbreviation=team.get("abbreviation") or None,
                    played=int(stats.get("gamesPlayed", wins + losses)),
                    wins=wins, losses=losses,
                    rank=int(stats.get("rank", position)),
                    games_back=str(stats["gamesBehind"]) if stats.get("gamesBehind") is not None else None))
            except (KeyError, TypeError, ValueError):
                continue
    if not result:
        raise ValueError("WNBA standings response contained no usable entries")
    return tuple(result)


def fetch_wnba_standings(_league="WNBA", *, opener=None, timeout=12):
    request = Request(URL, headers={"User-Agent": "UniversalLEDScoreboard/0.7"})
    with (opener or urlopen)(request, timeout=timeout) as response:
        return parse_wnba_standings(json.load(response))
