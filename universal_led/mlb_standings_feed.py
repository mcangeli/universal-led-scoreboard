"""MLB StatsAPI division standings adapter; no rendering-time requests."""
import json
from urllib.parse import urlencode
from urllib.request import urlopen

from .mlb_data import TEAM_ABBREVIATIONS
from .standings import Standing

DIVISIONS = {
    201: "AL EAST", 202: "AL CENTRAL", 200: "AL WEST",
    204: "NL EAST", 205: "NL CENTRAL", 203: "NL WEST",
}
DIVISION_KEYS = {
    201: "AL_EAST", 202: "AL_CENTRAL", 200: "AL_WEST",
    204: "NL_EAST", 205: "NL_CENTRAL", 203: "NL_WEST",
}
API = "https://statsapi.mlb.com/api/v1/standings"


def parse_mlb_standings(payload):
    """Preserve official division ranks; never guess MLB tiebreakers."""
    rows = []
    for division in payload.get("records", []):
        division_id = (division.get("division") or {}).get("id")
        if division_id not in DIVISIONS:
            continue
        for team in division.get("teamRecords", []):
            team_id = (team.get("team") or {}).get("id")
            rank = team.get("divisionRank")
            wins, losses = team.get("wins"), team.get("losses")
            try:
                rank = int(rank)
                wins = int(wins)
                losses = int(losses)
            except (TypeError, ValueError):
                continue
            if rank < 1 or wins < 0 or losses < 0:
                continue
            code = TEAM_ABBREVIATIONS.get(team_id)
            if code is None:
                code = str((team.get("team") or {}).get("abbreviation") or team_id)
            rows.append(Standing(
                league="MLB", group=DIVISION_KEYS[division_id],
                team_id=str(team_id), played=wins + losses,
                wins=wins, losses=losses, rank=rank,
                abbreviation=code[:3],
                games_back=str(team.get("divisionGamesBack", "-"))))
    return tuple(rows)


def fetch_mlb_standings(*, season=None, fetch=None):
    """Fetch official division standings. Caller supplies background cadence."""
    params = {"leagueId": "103,104", "standingsTypes": "regularSeason",
              "hydrate": "team"}
    if season is not None:
        params["season"] = int(season)
    url = API + "?" + urlencode(params)
    if fetch is None:
        def fetch(address):
            with urlopen(address, timeout=8) as response:
                return json.load(response)
    return parse_mlb_standings(fetch(url))

def fetch_mlb_group(division, *, fetcher=fetch_mlb_standings):
    """Adapt one official MLB division to the existing cached worker API."""
    if division not in DIVISION_KEYS.values():
        raise ValueError("Unknown MLB division")
    return tuple(row for row in fetcher() if row.group == division)
