"""ESPN-style soccer scoreboard normalization for MLS and NWSL.

Pure parsing only: network fetching and rotation integration are separate steps.
Missing scorer details remain unknown rather than being guessed.
"""
from collections.abc import Mapping

from .soccer import SoccerGoal, SoccerMatch, SUPPORTED_LEAGUES


def parse_scoreboard(payload: Mapping, league: str) -> tuple[SoccerMatch, ...]:
    """Normalize a scoreboard JSON response into league-neutral matches."""
    league = league.upper()
    if league not in SUPPORTED_LEAGUES:
        raise ValueError("Unsupported soccer league")
    matches = []
    for event in payload.get("events", []) or []:
        competitions = event.get("competitions") or []
        if not competitions:
            continue
        competition = competitions[0]
        teams = {}
        for entry in competition.get("competitors", []) or []:
            side = entry.get("homeAway")
            if side in ("home", "away"):
                team = entry.get("team") or {}
                teams[side] = (str(team.get("abbreviation") or team.get("id") or ""), _score(entry.get("score")))
        if "home" not in teams or "away" not in teams:
            continue
        status = event.get("status") or {}
        status_type = status.get("type") or {}
        state = str(status_type.get("state") or status_type.get("name") or "unknown").lower()
        # ESPN's status.type.state is normally "pre", "in", or "post".
        # Some provider snapshots only include the long status name.
        state = {
            "status_in_progress": "in",
            "status_halftime": "in",
            "status_end_period": "in",
            "status_scheduled": "pre",
            "status_final": "post",
            "status_full_time": "post",
            "status_postponed": "postponed",
            "status_canceled": "canceled",
        }.get(state, state)
        goals = []
        for detail in competition.get("details", []) or []:
            if not detail.get("scoringPlay"):
                continue
            event_id = detail.get("id")
            if event_id is None:
                continue
            team = detail.get("team") or {}
            scorer = _credited_scorer(detail)
            clock = detail.get("clock") or {}
            minute = clock.get("displayValue") or detail.get("displayClock")
            goals.append(SoccerGoal(
                event_id=str(event_id),
                team_id=str(team.get("abbreviation") or team.get("id") or ""),
                scorer=scorer,
                minute=str(minute) if minute is not None else None,
                own_goal=bool(detail.get("ownGoal", False)),
            ))
        matches.append(SoccerMatch(
            match_id=str(event.get("id") or competition.get("id") or ""),
            league=league,
            home_id=teams["home"][0],
            away_id=teams["away"][0],
            home_score=teams["home"][1],
            away_score=teams["away"][1],
            status=state,
            goals=tuple(goals),
        ))
    return tuple(matches)


def _score(value) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def _credited_scorer(detail: Mapping) -> str | None:
    # Do not treat an assist provider or arbitrary participant as the scorer.
    for athlete in detail.get("athletesInvolved") or []:
        if athlete.get("type", "").lower() in ("scorer", "goal", "goal scorer"):
            person = athlete.get("athlete") or {}
            return person.get("displayName") or person.get("fullName")
    # Some feeds place the credited player directly on the scoring event.
    athlete = detail.get("scorer") or {}
    if isinstance(athlete, Mapping):
        return athlete.get("displayName") or athlete.get("fullName")
    return None
