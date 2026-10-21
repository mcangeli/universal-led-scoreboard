"""ULS-wide scheduling policy for legacy Bullpen screen adapters.

This policy is deliberately independent of MLB and never executes a plugin.
The universal scheduler must make the final selection before calling a renderer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BullpenRole(str, Enum):
    SUPPLEMENTAL = "supplemental"
    MLB_GAME_LAYOUT = "mlb_game_layout"


@dataclass(frozen=True)
class BullpenSlot:
    role: BullpenRole
    sport: str | None = None
    game_id: str | None = None


def bullpen_slot_allowed(slot: BullpenSlot, *, any_live_game: bool,
                         selected_sport: str | None = None,
                         selected_game_id: str | None = None) -> bool:
    """Determine whether the universal coordinator may schedule a Bullpen frame.

    Supplemental screens are suppressed whenever *any* enabled sport is live.
    MLB game layouts may run only for the exact MLB game selected by ULS.
    """
    if slot.role == BullpenRole.SUPPLEMENTAL:
        return not any_live_game
    if slot.role == BullpenRole.MLB_GAME_LAYOUT:
        return (selected_sport == "mlb"
                and bool(selected_game_id)
                and slot.sport == "mlb"
                and slot.game_id == selected_game_id)
    return False
