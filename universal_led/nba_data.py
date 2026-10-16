"""Provider-independent NBA snapshots and ESPN scoreboard normalization."""
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class BasketballGame:
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

def _score(value):
    try:
        number = int(value)
        return number if number >= 0 and not isinstance(value, bool) else None
    except (TypeError, ValueError):
        return None

def _start(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc) if dt.tzinfo else None
    except (ValueError, AttributeError):
        return None

def parse_game(event):
    """Parse an ESPN NBA scoreboard event; reject malformed competitor records."""
    if not isinstance(event, dict):
        raise ValueError("NBA event must be an object")
    competitions = event.get("competitions")
    if not isinstance(competitions, list) or not competitions:
        raise ValueError("NBA event missing competition")
    competition = competitions[0]
    if not isinstance(competition, dict):
        raise ValueError("Invalid NBA competition")
    competitors = competition.get("competitors")
    if not isinstance(competitors, list):
        raise ValueError("Invalid NBA competitors")
    teams = {c.get("homeAway"): c for c in competitors if isinstance(c, dict)}
    if "home" not in teams or "away" not in teams:
        raise ValueError("NBA event missing home or away team")
    def team(side):
        obj = teams[side]
        data = obj.get("team") or {}
        if not isinstance(data, dict):
            raise ValueError("Invalid NBA team")
        abbr = str(data.get("abbreviation") or "UNK").upper()[:3]
        return abbr, str(data.get("displayName") or abbr), _score(obj.get("score"))
    def record(side):
        records = teams[side].get("records") or []
        if not isinstance(records, list):
            return ""
        for item in records:
            if isinstance(item, dict) and item.get("type") in ("total", "overall"):
                return str(item.get("summary") or "")[:12]
        return ""
    away, away_name, away_score = team("away")
    home, home_name, home_score = team("home")
    state = event.get("status") or competition.get("status") or {}
    state_type = state.get("type") or {}
    name = str(state_type.get("name") or "").upper()
    short = str(state_type.get("shortDetail") or state_type.get("detail") or "")
    if name in ("STATUS_POSTPONED", "STATUS_CANCELED"):
        status = "postponed"
    elif name in ("STATUS_FINAL", "STATUS_FULL_TIME"):
        status = "final"
    elif name in ("STATUS_IN_PROGRESS", "STATUS_HALFTIME", "STATUS_END_PERIOD"):
        status = "live"
    elif name in ("STATUS_SCHEDULED", "STATUS_DELAYED", "STATUS_PREGAME"):
        status = "scheduled"
    else:
        status = "unknown"
    period = state.get("period")
    if type(period) is not int or period < 1:
        period = None
    return BasketballGame(str(event["id"]), _start(event.get("date")),
        away, home, away_name, home_name, away_score, home_score,
        status, period, str(state.get("displayClock") or "") or None, short,
        record("away"), record("home"))

def parse_scoreboard(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("Invalid NBA scoreboard payload")
    return [parse_game(event) for event in payload["events"]]
