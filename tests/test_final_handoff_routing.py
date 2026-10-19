"""Opt-in final handoff rendering contract tests."""
import unittest
from types import SimpleNamespace
from universal_led.final_score_handoff import FinalScoreHandoff
from universal_led.multisport_runtime import MultiSportRenderer


class Sport:
    def frame(self):
        return "LIVE"
    def has_live_games(self):
        return True
    def frame_for_game(self, game):
        return "FINAL:" + game.game_id


class HandoffRoutingTests(unittest.TestCase):
    def test_final_handoff_draws_exact_game_for_full_slot(self):
        now = [0]
        queue = FinalScoreHandoff()
        queue.observe("nhl", [SimpleNamespace(game_id="7", status="live")],
                      id_getter=lambda g: g.game_id)
        queue.observe("nhl", [SimpleNamespace(game_id="7", status="final")],
                      id_getter=lambda g: g.game_id)
        board = MultiSportRenderer(Sport(), Sport(), active_sport="nhl",
                                   clock=lambda: now[0], final_handoff=queue)
        self.assertEqual(board.frame(), "FINAL:7")
        now[0] = 11
        self.assertEqual(board.frame(), "FINAL:7")
        now[0] = 12
        self.assertEqual(board.frame(), "LIVE")
        self.assertIsNone(queue.next())

    def test_disabled_sport_does_not_render_final(self):
        now = [0]
        queue = FinalScoreHandoff()
        queue.observe("nhl", [SimpleNamespace(game_id="7", status="live")],
                      id_getter=lambda g: g.game_id)
        queue.observe("nhl", [SimpleNamespace(game_id="7", status="final")],
                      id_getter=lambda g: g.game_id)
        board = MultiSportRenderer(Sport(), Sport(), active_sport="mlb",
                                   clock=lambda: now[0], final_handoff=queue)
        self.assertEqual(board.frame(), "LIVE")


if __name__ == "__main__":
    unittest.main()
