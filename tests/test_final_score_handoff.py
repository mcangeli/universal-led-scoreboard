"""Final-score transition and handoff queue regression tests."""
import unittest
from types import SimpleNamespace
from universal_led.final_score_handoff import FinalScoreHandoff


def game(id, status):
    return SimpleNamespace(game_id=id, status=status)


class FinalScoreHandoffTests(unittest.TestCase):
    def test_first_seen_final_does_not_replay(self):
        queue = FinalScoreHandoff()
        queue.observe("nhl", [game("1", "final")], id_getter=lambda g: g.game_id)
        self.assertIsNone(queue.next())

    def test_live_to_final_shown_once(self):
        queue = FinalScoreHandoff()
        queue.observe("nhl", [game("1", "live")], id_getter=lambda g: g.game_id)
        queue.observe("nhl", [game("1", "final")], id_getter=lambda g: g.game_id)
        self.assertEqual(queue.next()[0], ("nhl", "1"))
        self.assertEqual(queue.next()[0], ("nhl", "1"))
        queue.displayed()
        self.assertIsNone(queue.next())
        queue.observe("nhl", [game("1", "final")], id_getter=lambda g: g.game_id)
        self.assertIsNone(queue.next())

    def test_multiple_sports_queue_in_order(self):
        queue = FinalScoreHandoff(slots=2)
        for sport in ("mlb", "nfl"):
            queue.observe(sport, [game("same", "live")], id_getter=lambda g: g.game_id)
            queue.observe(sport, [game("same", "final")], id_getter=lambda g: g.game_id)
        self.assertEqual(queue.next()[0], ("mlb", "same"))
        queue.displayed()
        self.assertEqual(queue.next()[0], ("mlb", "same"))
        queue.displayed()
        self.assertEqual(queue.next()[0], ("nfl", "same"))
        queue.displayed()
        queue.displayed()
        self.assertIsNone(queue.next())

    def test_cancel_pending(self):
        queue = FinalScoreHandoff()
        queue.observe("nba", [game("7", "live")], id_getter=lambda g: g.game_id)
        queue.observe("nba", [game("7", "final")], id_getter=lambda g: g.game_id)
        queue.cancel("nba", "7")
        self.assertIsNone(queue.next())

    def test_invalid_slots(self):
        with self.assertRaises(ValueError):
            FinalScoreHandoff(slots=0)


if __name__ == "__main__":
    unittest.main()
