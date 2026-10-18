"""Optional English match-summary goal enrichment for background feed polling."""
import json
from dataclasses import replace
from urllib.request import Request, urlopen

from .english_football import COMPETITIONS
from .english_summary import parse_key_event_goals
from .soccer_rotation import is_live

BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"


def fetch_summary(league, match_id, *, opener=urlopen):
    if league not in COMPETITIONS or not str(match_id).isdigit():
        raise ValueError("Invalid English match summary request")
    request = Request(f"{BASE}/{COMPETITIONS[league]}/summary?event={match_id}",
                      headers={"Accept": "application/json",
                               "User-Agent": "UniversalLEDScoreboard/0.6"})
    with opener(request, timeout=5) as response:
        return json.load(response)


class EnglishGoalEnricher:
    """Enrich only live matches, leaving scoreboard snapshots usable on failure.

    Intended for a background SoccerFeed.refresh call, never frame().
    """

    def __init__(self, fetcher=fetch_summary):
        self.fetcher = fetcher
        self._last_goals = {}

    def __call__(self, match):
        if match.league not in COMPETITIONS or not is_live(match):
            return match
        key = (match.league, match.match_id)
        try:
            goals = parse_key_event_goals(self.fetcher(match.league, match.match_id))
        except (OSError, ValueError, TypeError, KeyError):
            # Keep previously confirmed goal IDs during temporary summary outages.
            # Otherwise an empty snapshot can cause later duplicate alerts.
            return replace(match, goals=self._last_goals.get(key, match.goals))
        self._last_goals[key] = goals
        return replace(match, goals=goals)
