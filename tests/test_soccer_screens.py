import unittest

from universal_led.soccer import SoccerGoal, SoccerMatch
from universal_led.soccer_screens import goal_screen, match_screen


class SoccerScreenTests(unittest.TestCase):
    def match(self, league="MLS"):
        return SoccerMatch("m1", league, "ATL", "MIA", 2, 1, "live")

    def test_match_screen_has_scores_and_league(self):
        screen = match_screen(self.match())
        self.assertEqual(screen.kind, "match")
        self.assertEqual(screen.header, "MLS")
        self.assertIn("MIA", screen.line1)
        self.assertIn("ATL", screen.line2)
        self.assertIn("2", screen.line2)

    def test_live_match_shows_half_and_clock(self):
        game = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "in", clock="67'", period=2)
        self.assertEqual(match_screen(game).footer, "2H 67'")

    def test_live_without_clock_shows_live(self):
        game = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "in")
        self.assertEqual(match_screen(game).footer, "LIVE")

    def test_final_shows_final(self):
        game = SoccerMatch("m1", "NWSL", "ATL", "MIA", 2, 1, "post")
        self.assertEqual(match_screen(game).footer, "FINAL")

    def test_stoppage_time_preserved(self):
        game = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "in", clock="90+3'", period=2)
        self.assertEqual(match_screen(game).footer, "2H 90+3'")

    def test_first_half_stoppage_clock_removes_extra_apostrophe(self):
        game = SoccerMatch("m1", "MLS", "CLT", "PHI", 0, 1, "in", clock="45'+1'", period=1)
        self.assertEqual(match_screen(game).footer, "1H 45+1'")

    def test_second_half_stoppage_clock_removes_extra_apostrophe(self):
        game = SoccerMatch("m1", "NWSL", "ATL", "MIA", 1, 1, "in", clock="90' + 3'", period=2)
        self.assertEqual(match_screen(game).footer, "2H 90+3'")

    def test_halftime_displays_ht_instead_of_stale_clock(self):
        game = SoccerMatch("m1", "NWSL", "ATL", "MIA", 1, 1, "halftime", clock="45'", period=1)
        self.assertEqual(match_screen(game).footer, "HT")

    def test_interrupted_match_keeps_league_and_score(self):
        for league in ("MLS", "NWSL", "EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO"):
            with self.subTest(league=league):
                game = SoccerMatch("m1", league, "ATL", "MIA", 2, 1, "rain_delay")
                screen = match_screen(game)
                self.assertEqual(screen.header, {"CHAMPIONSHIP": "EFL CH", "LEAGUE_ONE": "EFL L1", "LEAGUE_TWO": "EFL L2"}.get(league, league))
                self.assertEqual(screen.footer, "DELAYED")
                self.assertIn("2", screen.line2)

    def test_english_division_headings_preserve_pregame_records_and_kickoff(self):
        for league, heading in (("EPL", "EPL"), ("CHAMPIONSHIP", "EFL CH"),
                                ("LEAGUE_ONE", "EFL L1"), ("LEAGUE_TWO", "EFL L2")):
            with self.subTest(league=league):
                game = SoccerMatch("m1", league, "FLE", "CNL", 0, 0, "pre",
                                   away_record="3-5-3", home_record="4-3-4",
                                   kickoff="2026-10-20T18:45:00Z")
                screen = match_screen(game, timezone="America/New_York")
                self.assertEqual(screen.header, heading)
                self.assertEqual(screen.line1, "CNL 4-3-4")
                self.assertEqual(screen.line2, "FLE 3-5-3")
                self.assertEqual(screen.footer, "2:45PM")

    def test_interruption_aliases_use_readable_status(self):
        for raw, expected in (("ppd", "POSTPONED"), ("rescheduled", "RESCHEDULED"),
                              ("susp", "SUSPENDED")):
            with self.subTest(raw=raw):
                game = SoccerMatch("m1", "EPL", "ARS", "CHE", 0, 0, raw)
                self.assertEqual(match_screen(game).footer, expected)

    def test_nwsl_match_uses_shared_layout(self):
        self.assertEqual(match_screen(self.match("NWSL")).header, "NWSL")

    def test_credited_scorer_is_displayed(self):
        screen = goal_screen(self.match(), SoccerGoal("g1", "ATL", "Alex Forward", "67'"))
        self.assertEqual(screen.header, "GOAL!")
        self.assertEqual(screen.line1, "Alex Forward")
        self.assertIn("67'", screen.line2)

    def test_missing_scorer_falls_back_to_team(self):
        screen = goal_screen(self.match(), SoccerGoal("g2", "MIA"))
        self.assertEqual(screen.line1, "MIA")

    def test_own_goal_is_labeled(self):
        screen = goal_screen(self.match(), SoccerGoal("g3", "ATL", "Defender", "81'", True))
        self.assertEqual(screen.header, "OWN GOAL")

    def test_long_scorer_is_bounded(self):
        screen = goal_screen(self.match(), SoccerGoal("g4", "ATL", "Extremely Long Player Name"))
        self.assertLessEqual(len(screen.line1), 16)

    def test_score_is_present_on_goal_screen(self):
        screen = goal_screen(self.match("NWSL"), SoccerGoal("g5", "ATL"))
        self.assertIn("1-2", screen.footer)
        self.assertIn("NWSL", screen.footer)


if __name__ == "__main__":
    unittest.main()
