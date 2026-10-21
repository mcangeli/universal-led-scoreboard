"""Guardrails for Bullpen compatibility across the universal sport scheduler."""
import unittest

from universal_led.bullpen_policy import BullpenRole, BullpenSlot, bullpen_slot_allowed


class BullpenPolicyTests(unittest.TestCase):
    def test_supplemental_suppressed_during_any_live_sport(self):
        slot = BullpenSlot(BullpenRole.SUPPLEMENTAL)
        for sport in ("mlb", "nba", "nfl", "nhl", "mls", "epl"):
            with self.subTest(sport=sport):
                self.assertFalse(bullpen_slot_allowed(
                    slot, any_live_game=True, selected_sport=sport))

    def test_supplemental_allowed_without_live_games(self):
        self.assertTrue(bullpen_slot_allowed(
            BullpenSlot(BullpenRole.SUPPLEMENTAL), any_live_game=False))

    def test_mlb_layout_only_for_selected_mlb_game(self):
        slot = BullpenSlot(BullpenRole.MLB_GAME_LAYOUT, sport="mlb", game_id="123")
        self.assertTrue(bullpen_slot_allowed(
            slot, any_live_game=True, selected_sport="mlb", selected_game_id="123"))
        self.assertFalse(bullpen_slot_allowed(
            slot, any_live_game=True, selected_sport="mlb", selected_game_id="456"))
        self.assertFalse(bullpen_slot_allowed(
            slot, any_live_game=True, selected_sport="nhl", selected_game_id="123"))

    def test_mlb_layout_requires_game_selection(self):
        slot = BullpenSlot(BullpenRole.MLB_GAME_LAYOUT, sport="mlb", game_id="123")
        self.assertFalse(bullpen_slot_allowed(
            slot, any_live_game=False, selected_sport="mlb"))
        self.assertFalse(bullpen_slot_allowed(
            BullpenSlot(BullpenRole.MLB_GAME_LAYOUT, sport="mlb"),
            any_live_game=False, selected_sport="mlb", selected_game_id="123"))


if __name__ == "__main__":
    unittest.main()
