"""NFL division standings from ESPN's official-rank standings response.

This module is independent of the board's frame loop; background caches own I/O.
"""
import json
from urllib.request import Request, urlopen

from .standings import Standing

NFL_STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
NFL_DIVISIONS = ("AFC East", "AFC North", "AFC South", "AFC West",
                 "NFC East", "NFC North", "NFC South", "NFC West")


# ESPN's current endpoint returns conference-level entries rather than
# nested divisions. Keep division membership explicit and independent of
# team display names. NFL.com standings require authenticated access.
NFL_TEAM_DIVISIONS = {
    "BUF": "AFC East", "MIA": "AFC East", "NE": "AFC East", "NYJ": "AFC East",
    "BAL": "AFC North", "CIN": "AFC North", "CLE": "AFC North", "PIT": "AFC North",
    "HOU": "AFC South", "IND": "AFC South", "JAX": "AFC South", "JAC": "AFC South",
    "TEN": "AFC South",
    "DEN": "AFC West", "KC": "AFC West", "LAC": "AFC West", "LV": "AFC West",
    "DAL": "NFC East", "NYG": "NFC East", "PHI": "NFC East", "WSH": "NFC East",
    "WAS": "NFC East",
    "CHI": "NFC North", "DET": "NFC North", "GB": "NFC North", "MIN": "NFC North",
    "ATL": "NFC South", "CAR": "NFC South", "NO": "NFC South", "TB": "NFC South",
    "ARI": "NFC West", "LA": "NFC West", "LAR": "NFC West",
    "SF": "NFC West", "SEA": "NFC West",
}

def _stat(entry, name):
    for item in entry.get("stats", []):
        if item.get("name") == name:
            return item.get("value")
    return None


def parse_nfl_standings(payload):
    """Preserve provider division order and its W-L-T totals."""
    if not isinstance(payload, dict) or not isinstance(payload.get("children"), list):
        raise ValueError("Invalid NFL standings response")
    grouped = {division: [] for division in NFL_DIVISIONS}
    for conference in payload["children"]:
        if not isinstance(conference, dict):
            continue
        divisions = conference.get("children") or []
        # Older ESPN payloads nested divisions; current responses provide
        # standings directly on the AFC/NFC conference objects.
        sources = divisions if divisions else [conference]
        for source in sources:
            if not isinstance(source, dict):
                continue
            explicit_group = source.get("name") if source.get("name") in NFL_DIVISIONS else None
            entries = (source.get("standings") or {}).get("entries", [])
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                team = entry.get("team") or {}
                code = team.get("abbreviation")
                if not isinstance(code, str):
                    continue
                code = code.upper()
                group = explicit_group or NFL_TEAM_DIVISIONS.get(code)
                if group is None:
                    continue
                values = [_stat(entry, key) for key in ("wins", "losses", "ties")]
                if any(type(value) not in (int, float) or value < 0 or
                       int(value) != value for value in values):
                    continue
                wins, losses, ties = map(int, values)
                grouped[group].append((code, str(team.get("id", code)), wins, losses, ties))
    rows = []
    for group in NFL_DIVISIONS:
        records = grouped[group]
        # ESPN conference entries do not give division ranks. Sort records
        # by win percentage as a provisional division order; tied records
        # may differ from official NFL tiebreaker rankings.
        records.sort(key=lambda r: (-(r[2] + r[4] / 2) /
                                   max(1, r[2] + r[3] + r[4]), -r[2], r[0]))
        for rank, (code, team_id, wins, losses, ties) in enumerate(records, 1):
            rows.append(Standing(
                league="NFL", group=group, team_id=team_id,
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
