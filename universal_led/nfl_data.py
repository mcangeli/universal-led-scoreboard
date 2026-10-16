"""Provider-independent NFL game snapshots and ESPN scoreboard normalization."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class FootballGame:
    game_id: str
    start_utc: datetime | None
    away: str
    home: str
    away_name: str
    home_name: str
    away_score: int | None
    home_score: int | None
    status: str
    period: int | None = None
    clock: str | None = None
    detail: str = ""
    away_record: str = ""
    home_record: str = ""
    possession: str = ""
    down: int | None = None
    distance: int | None = None

def _score(value):
    try:
        return int(value) if not isinstance(value, bool) and int(value) >= 0 else None
    except (TypeError, ValueError):
        return None

def _start(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc) if dt.tzinfo else None
    except (ValueError, AttributeError):
        return None

def parse_game(event):
    if not isinstance(event, dict):
        raise ValueError("NFL event must be an object")
    competitions = event.get("competitions")
    if not isinstance(competitions, list) or not competitions or not isinstance(competitions[0], dict):
        raise ValueError("NFL event missing competition")
    competition = competitions[0]
    competitors = competition.get("competitors")
    if not isinstance(competitors, list):
        raise ValueError("NFL event missing competitors")
    teams = {item.get("homeAway"): item for item in competitors if isinstance(item, dict)}
    if "home" not in teams or "away" not in teams:
        raise ValueError("NFL event missing home or away team")
    def team(side):
        obj = teams[side]
        data = obj.get("team") or {}
        if not isinstance(data, dict):
            raise ValueError("Invalid NFL team")
        abbr = str(data.get("abbreviation") or "UNK").upper()[:3]
        return abbr, str(data.get("displayName") or abbr), _score(obj.get("score"))
    def record(side):
        for item in teams[side].get("records") or []:
            if isinstance(item, dict) and item.get("type") in ("total", "overall"):
                return str(item.get("summary") or "")[:12]
        return ""
    away, away_name, away_score = team("away")
    home, home_name, home_score = team("home")
    state = event.get("status") or competition.get("status") or {}
    state_type = state.get("type") or {}
    name = str(state_type.get("name") or "").upper()
    detail = str(state_type.get("shortDetail") or state_type.get("detail") or "")
    if name in ("STATUS_FINAL", "STATUS_FULL_TIME"):
        status = "final"
    elif name in ("STATUS_POSTPONED", "STATUS_CANCELED"):
        status = "postponed"
    elif name in ("STATUS_IN_PROGRESS", "STATUS_HALFTIME", "STATUS_END_PERIOD"):
        status = "live"
    elif name in ("STATUS_SCHEDULED", "STATUS_PREGAME", "STATUS_DELAYED"):
        status = "scheduled"
    else:
        status = "unknown"
    period = state.get("period")
    if type(period) is not int or period < 1:
        period = None
    possession = ""
    for side in ("away", "home"):
        if teams[side].get("id") is not None and str(teams[side]["id"]) == str((competition.get("situation") or {}).get("possession")):
            possession = away if side == "away" else home
    situation = competition.get("situation") or {}
    down = situation.get("down")
    distance = situation.get("distance")
    down = down if type(down) is int and 1 <= down <= 4 else None
    distance = distance if type(distance) is int and distance >= 0 else None
    return FootballGame(str(event["id"]), _start(event.get("date")), away, home,
        away_name, home_name, away_score, home_score, status, period,
        str(state.get("displayClock") or "") or None, detail, record("away"), record("home"),
        possession, down, distance)

def parse_scoreboard(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("Invalid NFL scoreboard payload")
    return [parse_game(event) for event in payload["events"]]
