"""Soccer screen scheduling helpers for the universal multi-sport rotation.

These pure functions are designed for the existing scheduler to call. They do
not modify its priorities or access matrix hardware directly.
"""
from collections.abc import Iterable

from .soccer import SoccerMatch
from .game_interruptions import InterruptionPolicy, show_interruption


LIVE_STATES = frozenset(("in", "live", "in_progress", "inprogress", "halftime"))
FINAL_STATES = frozenset(("post", "final", "completed", "complete"))


def is_live(match: SoccerMatch) -> bool:
    return match.status.strip().lower() in LIVE_STATES


def eligible_matches(
    matches: Iterable[SoccerMatch],
    *,
    favorites: Iterable[str] = (),
    mode: str = "all",
    interruption_policy: InterruptionPolicy | None = None,
    has_live_games: bool | None = None,
) -> tuple[SoccerMatch, ...]:
    """Filter soccer matches by team favorites, without changing game status."""
    if mode not in ("all", "favorites", "fallback"):
        raise ValueError("Unknown soccer selection mode")
    games = tuple(matches)
    live_present = any(is_live(game) for game in games) if has_live_games is None else has_live_games
    games = tuple(game for game in games if show_interruption(
        game.status, has_live_games=live_present, policy=interruption_policy))
    if mode == "all":
        return games
    favorite_ids = {str(team).strip().upper() for team in favorites if str(team).strip()}
    # Match MLB/NHL/NBA behavior: with no favorites configured, show all games
    # rather than leaving the display blank in favorites-only mode.
    if not favorite_ids:
        return games
    selected = tuple(
        match for match in games
        if any(identifier.strip().upper() in favorite_ids for identifier in (match.home_id, match.away_id, match.home_club_key or '', match.away_club_key or ''))
    )
    if mode == "favorites":
        return selected
    live = tuple(match for match in games if is_live(match))
    if live:
        favorite_live = tuple(match for match in selected if is_live(match))
        return favorite_live or live
    return selected or games


def prioritize_live(matches: Iterable[SoccerMatch]) -> tuple[SoccerMatch, ...]:
    """Keep only live matches when any are live; otherwise retain all."""
    games = tuple(matches)
    live = tuple(game for game in games if is_live(game))
    return live if live else games
