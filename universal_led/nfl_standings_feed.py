"""NFL division standings from ESPN's official-rank standings response.

This module is independent of the board's frame loop; background caches own I/O.
"""
import json
from urllib.request import Request, urlopen

from .standings import Standing

NFL_STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
NFL_DIVISIONS = ("AFC East", "AFC North", "AFC South", "AFC West",
                 "NFC East", "NFC North", "NFC South", "NFC West")


def _stat(entry, name):
    for item in entry.get("stats", []):
        if item.get("name") == name:
            return item.get("value")
    return None


def parse_nfl_standings(payload):
    """Preserve provider division order and its W-L-T totals."""
    if not isinstance(payload, dict) or not isinstance(payload.get("children"), list):
        raise ValueError("Invalid NFL standings response")
    rows = []
    for conference in payload["children"]:
        for division in conference.get("children", []):
            name = division.get("name", "")
            if name not in NFL_DIVISIONS:
                continue
            entries = division.get("standings", {}).get("entries", [])
            for rank, entry in enumerate(entries, 1):
                team = entry.get("team", {})
                code = team.get("abbreviation")
                values = [_stat(entry, key) for key in ("wins", "losses", "ties")]
                if not isinstance(code, str) or any(
                        type(value) not in (int, float) or value < 0 or int(value) != value
                        for value in values):
                    continue
                wins, losses, ties = map(int, values)
                rows.append(Standing(
                    league="NFL", group=name, team_id=str(team.get("id", code)),
                    abbreviation=code, played=wins + losses + ties,
                    wins=wins, losses=losses, draws=ties, rank=rank))
    return tuple(rows)


def fetch_nfl_standings(_league="NFL", *, opener=None, timeout=12):
    if opener is None:
        opener = urlopen
    request = Request(NFL_STANDINGS_URL, headers={
        "User-Agent": "Mozilla/5.0 (compatible; UniversalLEDScoreboard/0.7)",
        "Accept": "application/json",
    })
    with opener(request, timeout=timeout) as response:
        return parse_nfl_standings(json.load(response))


def fetch_nfl_division(division, *, fetcher=fetch_nfl_standings):
    if division not in NFL_DIVISIONS:
        raise ValueError("Unknown NFL division")
    return tuple(row for row in fetcher("NFL") if row.group == division)
