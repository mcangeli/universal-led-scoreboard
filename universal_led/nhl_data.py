"""Provider-independent NHL game snapshots and NHL score payload adapter.

This module deliberately has no network or renderer dependencies. API transport,
caching, and matrix presentation are separate responsibilities.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class HockeyGame:
    game_id: int
    start_utc: datetime | None
    away: str
    home: str
    away_name: str
    home_name: str
    away_score: int | None
    home_score: int | None
    status: str
    period: int | None = None
    period_label: str | None = None
    clock: str | None = None
    intermission: bool = False
    shootout: bool = False


def _team(value: Any) -> tuple[str, str]:
    obj = value if isinstance(value, dict) else {}
    abbreviation = str(obj.get("abbrev") or "UNK").strip().upper()
    name_value = obj.get("name") or {}
    name = (name_value.get("default") if isinstance(name_value, dict) else name_value) or abbreviation
    return abbreviation[:3], str(name)


def _score(value: Any) -> int | None:
    if type(value) is int and value >= 0:
        return value
    return None


def _start(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
    except ValueError:
        return None


def _status(value: Any) -> str:
    code = str(value or "").upper()
    if code in ("LIVE", "CRIT"):
        return "live"
    if code in ("FINAL", "OFF"):
        return "final"
    if code in ("FUT", "PRE"):
        return "scheduled"
    if code in ("PPD", "POSTPONED"):
        return "postponed"
    return "unknown"


def parse_game(item: dict[str, Any]) -> HockeyGame:
    """Normalize one entry from the NHL v1 score endpoint.

    No network calls occur here. Missing scores remain unknown, not zero.
    """
    if not isinstance(item, dict):
        raise ValueError("NHL game must be an object")
    away_obj = item.get("awayTeam") or {}
    home_obj = item.get("homeTeam") or {}
    away, away_name = _team(away_obj)
    home, home_name = _team(home_obj)
    period_descriptor = item.get("periodDescriptor") or {}
    if not isinstance(period_descriptor, dict):
        period_descriptor = {}
    period = period_descriptor.get("number")
    if type(period) is not int or period < 1:
        period = None
    label = period_descriptor.get("periodType")
    label = str(label).upper() if label else None
    clock_obj = item.get("clock") or {}
    if not isinstance(clock_obj, dict):
        clock_obj = {}
    clock = clock_obj.get("timeRemaining")
    clock = str(clock) if clock is not None else None
    return HockeyGame(
        game_id=int(item["id"]),
        start_utc=_start(item.get("startTimeUTC")),
        away=away, home=home, away_name=away_name, home_name=home_name,
        away_score=_score(away_obj.get("score")),
        home_score=_score(home_obj.get("score")),
        status=_status(item.get("gameState")),
        period=period, period_label=label, clock=clock,
        intermission=clock_obj.get("inIntermission") is True,
        shootout=label == "SO",
    )


def parse_scoreboard(payload: dict[str, Any]) -> list[HockeyGame]:
    """Parse NHL /v1/score/{date} response, preserving schedule order."""
    if not isinstance(payload, dict) or not isinstance(payload.get("games", []), list):
        raise ValueError("Invalid NHL scoreboard payload")
    return [parse_game(game) for game in payload.get("games", [])]
