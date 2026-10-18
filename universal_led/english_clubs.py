"""Cached ESPN club directory for all four English divisions."""
import json
import threading
import time
from urllib.request import Request, urlopen
from .english_football import COMPETITIONS

_CACHE = {"at": 0.0, "clubs": []}
_LOCK = threading.Lock()
TTL = 6 * 3600


def parse_teams(payload, division):
    if division not in COMPETITIONS:
        raise ValueError("Unsupported English division")
    clubs = []
    for sport in payload.get("sports", []):
        for league in sport.get("leagues", []):
            for entry in league.get("teams", []):
                team = entry.get("team", {})
                identifier = str(team.get("id", "")).strip()
                name = str(team.get("displayName") or team.get("name") or "").strip()
                if identifier.isdigit() and name:
                    clubs.append({"key": "espn:" + identifier, "name": name,
                                  "division": division})
    return clubs


def fetch_clubs(*, opener=urlopen):
    result = {}
    for division, slug in COMPETITIONS.items():
        request = Request(
            f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/teams",
            headers={"User-Agent": "UniversalLEDScoreboard/0.6", "Accept": "application/json"},
        )
        with opener(request, timeout=5) as response:
            payload = json.load(response)
        for club in parse_teams(payload, division):
            result[club["key"]] = club
    return sorted(result.values(), key=lambda item: (item["name"].casefold(), item["key"]))


def cached_clubs():
    with _LOCK:
        if _CACHE["clubs"] and time.monotonic() - _CACHE["at"] < TTL:
            return list(_CACHE["clubs"])
        try:
            clubs = fetch_clubs()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            if _CACHE["clubs"]:
                return list(_CACHE["clubs"])
            raise RuntimeError("Unable to retrieve ESPN English club directory") from exc
        _CACHE.update(at=time.monotonic(), clubs=clubs)
        return list(clubs)
