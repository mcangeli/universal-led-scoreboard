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
        if not isinstance(event, Mapping):
            continue
        competitions = event.get("competitions") or []
        if not competitions:
            continue
        competition = competitions[0]
        if not isinstance(competition, Mapping):
            continue
        teams = {}
        records = {}
        for entry in competition.get("competitors", []) or []:
            if not isinstance(entry, Mapping):
                continue
            side = entry.get("homeAway")
            if side in ("home", "away"):
                team = entry.get("team") or {}
                teams[side] = (_team_id(team), _score(entry.get("score")))
                records[side] = _team_record(entry)
        if "home" not in teams or "away" not in teams or not teams["home"][0] or not teams["away"][0]:
            continue
        status = event.get("status") or {}
        status_type = status.get("type") or {}
        state = str(status_type.get("state") or status_type.get("name") or "unknown").lower()
        # Match status detail may contain stoppage-time or halftime labels.
        # Keep halftime in the live rotation, even when ESPN supplies "in".
        # Some feeds report half-time as a descriptive phrase rather than a code.
        # ESPN can report state="in" alongside name="STATUS_HALFTIME".
        phase_fields = (
            status_type.get("name"), status_type.get("description"),
            status_type.get("detail"), status_type.get("shortDetail"),
            status.get("detail"), status.get("shortDetail"),
        )
        if state in ("in", "live", "in_progress", "inprogress") and any(
            isinstance(value, str) and value.strip().lower().replace("_", " ") in
            ("status halftime", "halftime", "half time", "ht", "half-time")
            for value in phase_fields
        ):
            state = "halftime"
        # ESPN's status.type.state is normally "pre", "in", or "post".
        # Some provider snapshots only include the long status name.
        state = {
            "status_in_progress": "in",
            "status_halftime": "halftime",
            "status_end_period": "in",
            "status_scheduled": "pre",
            "status_final": "post",
            "status_full_time": "post",
            "status_postponed": "postponed",
            "status_canceled": "canceled",
        }.get(state, state)
        goals = []
        for detail in competition.get("details", []) or []:
            if not isinstance(detail, Mapping) or not detail.get("scoringPlay"):
                continue
            event_id = detail.get("id")
            if event_id is None:
                continue
            team = detail.get("team") or {}
            scorer = _credited_scorer(detail)
            clock = detail.get("clock") or {}
            minute = (clock.get("displayValue") if isinstance(clock, Mapping) else None) or detail.get("displayClock")
            goals.append(SoccerGoal(
                event_id=str(event_id),
                team_id=_team_id(team),
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
            clock=_match_clock(status, competition),
            period=_match_period(status, competition),
            home_club_key=_english_club_key(competition, "home") if league in ("EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO") else None,
            away_club_key=_english_club_key(competition, "away") if league in ("EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO") else None,
            kickoff=event.get("date") or competition.get("date"),
            home_record=records.get("home"),
            away_record=records.get("away"),
        ))
    return tuple(matches)


def _team_id(team) -> str:
    """Prefer ESPN abbreviations and normalize them for favorite-team matching."""
    if not isinstance(team, Mapping):
        return ""
    return str(team.get("abbreviation") or team.get("id") or "").strip().upper()


def _score(value) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def _credited_scorer(detail: Mapping) -> str | None:
    # Do not treat an assist provider or arbitrary participant as the scorer.
    for athlete in detail.get("athletesInvolved") or []:
        if not isinstance(athlete, Mapping):
            continue
        if str(athlete.get("type") or "").lower() in ("scorer", "goal", "goal scorer"):
            person = athlete.get("athlete") or {}
            return person.get("displayName") or person.get("fullName")
    # Some feeds place the credited player directly on the scoring event.
    athlete = detail.get("scorer") or {}
    if isinstance(athlete, Mapping):
        return athlete.get("displayName") or athlete.get("fullName")
    return None


def _match_clock(status, competition):
    for source in (status, competition.get("status") or {}):
        if not isinstance(source, Mapping):
            continue
        clock = source.get("clock")
        value = source.get("displayClock")
        if not value and isinstance(clock, Mapping):
            value = clock.get("displayValue")
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _match_period(status, competition):
    for source in (status, competition.get("status") or {}, competition):
        if not isinstance(source, Mapping):
            continue
        value = source.get("period")
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _english_club_key(competition, side):
    for entry in competition.get("competitors") or []:
        if isinstance(entry, Mapping) and entry.get("homeAway") == side:
            team = entry.get("team") or {}
            if isinstance(team, Mapping) and team.get("id") is not None:
                value = str(team["id"]).strip()
                return f"espn:{value}" if value else None
    return None


def _team_record(entry):
    """Normalize provider soccer records to wins-draws-losses.

    ESPN soccer summaries are commonly wins-draws-losses; prefer named
    statistics when present, and only accept a well-formed total summary.
    """
    import re

    records = entry.get("records") or []
    if not isinstance(records, (list, tuple)):
        return None
    for record in records:
        if not isinstance(record, Mapping):
            continue
        stats = {
            str(stat.get("name", "")).lower(): stat.get("value")
            for stat in record.get("stats", [])
            if isinstance(stat, Mapping)
        }
        if all(key in stats for key in ("wins", "losses")) and (
            "ties" in stats or "draws" in stats
        ):
            try:
                wins = int(stats["wins"])
                losses = int(stats["losses"])
                draws = int(stats.get("ties", stats.get("draws")))
                if min(wins, losses, draws) >= 0:
                    return f"{wins}-{draws}-{losses}"
            except (ValueError, TypeError):
                pass
        # ESPN's soccer record summary uses W-D-L. Avoid interpreting
        # home/away or other split records as the full-season record.
        kind = str(record.get("type") or record.get("name") or "").lower()
        if kind not in ("total", "overall", "total record"):
            continue
        summary = record.get("summary")
        if isinstance(summary, str) and re.fullmatch(r"\\s*\\d+-\\d+-\\d+\\s*", summary):
            wins, draws, losses = map(int, summary.strip().split("-"))
            return f"{wins}-{draws}-{losses}"
    return None
