"""English football 64x32 match lifecycle acceptance tests.

All four divisions use the same shared soccer renderer. No network or matrix
hardware is needed to test the status/score/goal contracts.
"""
import unittest

from universal_led.soccer_feed import parse_scoreboard
from universal_led.soccer_screens import match_screen
from universal_led.soccer_rotation import is_live
from universal_led.soccer_display import SoccerDisplayController

DIVISIONS = ("EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO")


def payload(state, name, *, clock=None, period=None, score="0", details=()):
    status = {"type": {"state": state, "name": name}}
    if clock is not None:
        status["displayClock"] = clock
    if period is not None:
        status["period"] = period
    return {"events": [{"id": "fixture1", "status": status, "competitions": [{
        "competitors": [
            {"homeAway": "home", "team": {"id": "381", "abbreviation": "HOME"}, "score": score},
            {"homeAway": "away", "team": {"id": "382", "abbreviation": "AWAY"}, "score": "1"},
        ], "details": list(details)}]}]}


class EnglishMatchAcceptanceTests(unittest.TestCase):
    def test_scheduled_live_halftime_and_final_in_every_division(self):
        cases = [
            ("pre", "STATUS_SCHEDULED", None, None, "PRE", False),
            ("in", "STATUS_IN_PROGRESS", "24:11", 1, "1H 24:11", True),
            ("in", "STATUS_HALFTIME", None, 1, "HT", True),
            ("in", "STATUS_IN_PROGRESS", "90'+3'", 2, "2H 90+3'", True),
            ("post", "STATUS_FINAL", None, 2, "FINAL", False),
        ]
        for league in DIVISIONS:
            for state, name, clock, period, footer, live in cases:
                with self.subTest(league=league, status=name, clock=clock):
                    game, = parse_scoreboard(payload(state, name, clock=clock, period=period), league)
                    self.assertEqual(match_screen(game).footer, footer)
                    self.assertEqual(is_live(game), live)
                    self.assertEqual(game.home_club_key, "espn:381")
                    self.assertEqual(game.away_club_key, "espn:382")

    def test_new_goal_appears_then_returns_to_score(self):
        goal = {"id": "goal1", "scoringPlay": True, "team": {"abbreviation": "HOME"},
                "clock": {"displayValue": "56'"},
                "athletesInvolved": [{"type": "scorer", "athlete": {"displayName": "Example Scorer"}}]}
        game, = parse_scoreboard(payload("in", "STATUS_IN_PROGRESS", clock="56:00",
                                          period=2, score="2", details=[goal]), "EPL")
        display = SoccerDisplayController(goal_seconds=3)
        display.update(game)
        self.assertEqual(display.screen(game, 10).kind, "goal")
        self.assertEqual(display.screen(game, 14).kind, "match")
        display.update(game)
        self.assertEqual(display.screen(game, 15).kind, "match")

    def test_halftime_does_not_announce_late_feed_correction(self):
        goal = {"id": "goal1", "scoringPlay": True, "team": {"abbreviation": "HOME"}}
        game, = parse_scoreboard(payload("in", "STATUS_HALFTIME", details=[goal]), "CHAMPIONSHIP")
        display = SoccerDisplayController()
        display.update(game)
        self.assertEqual(display.screen(game, 1).kind, "match")


if __name__ == "__main__":
    unittest.main()
