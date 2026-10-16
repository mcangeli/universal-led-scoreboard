"""Offline NHL adapter regression tests."""
import unittest
from datetime import timezone

from universal_led.nhl_data import parse_game, parse_scoreboard


def sample(**changes):
    game = {
        "id": 2026020001,
        "startTimeUTC": "2026-10-16T23:00:00Z",
        "gameState": "FUT",
        "awayTeam": {"abbrev": "BOS", "name": {"default": "Boston Bruins"}},
        "homeTeam": {"abbrev": "NYR", "name": {"default": "New York Rangers"}},
    }
    game.update(changes)
    return game


class NHLDataTests(unittest.TestCase):
    def test_pregame_scores_are_unknown(self):
        game = parse_game(sample())
        self.assertEqual(game.status, "scheduled")
        self.assertIsNone(game.away_score)
        self.assertEqual(game.away, "BOS")
        self.assertEqual(game.home_name, "New York Rangers")
        self.assertEqual(game.start_utc.tzinfo, timezone.utc)

    def test_live_clock_and_period(self):
        game = parse_game(sample(
            gameState="LIVE",
            awayTeam={"abbrev": "BOS", "score": 2},
            homeTeam={"abbrev": "NYR", "score": 1},
            periodDescriptor={"number": 3, "periodType": "REG"},
            clock={"timeRemaining": "04:32", "inIntermission": False},
        ))
        self.assertEqual((game.away_score, game.home_score), (2, 1))
        self.assertEqual((game.period, game.clock), (3, "04:32"))
        self.assertEqual(game.status, "live")

    def test_overtime_and_shootout(self):
        ot = parse_game(sample(gameState="LIVE", periodDescriptor={"number": 4, "periodType": "OT"}))
        so = parse_game(sample(gameState="FINAL", periodDescriptor={"number": 5, "periodType": "SO"}))
        self.assertEqual(ot.period_label, "OT")
        self.assertTrue(so.shootout)
        self.assertEqual(so.status, "final")

    def test_intermission_and_postponement(self):
        game = parse_game(sample(gameState="LIVE", clock={"inIntermission": True}))
        self.assertTrue(game.intermission)
        self.assertEqual(parse_game(sample(gameState="PPD")).status, "postponed")

    def test_missing_fields_are_safe(self):
        game = parse_game({"id": 9})
        self.assertEqual(game.status, "unknown")
        self.assertEqual(game.away, "UNK")
        self.assertIsNone(game.start_utc)
        self.assertIsNone(game.period)

    def test_scoreboard_order(self):
        games = parse_scoreboard({"games": [sample(id=1), sample(id=2)]})
        self.assertEqual([g.game_id for g in games], [1, 2])

    def test_invalid_payload(self):
        with self.assertRaises(ValueError):
            parse_scoreboard({"games": {}})
        with self.assertRaises(ValueError):
            parse_game(None)


if __name__ == "__main__":
    unittest.main()
