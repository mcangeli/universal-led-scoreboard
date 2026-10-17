"""Release-level MLS/NWSL scenarios using provider-shaped ESPN snapshots."""
import unittest

from universal_led.soccer_feed import parse_scoreboard
from universal_led.soccer_rotation import eligible_matches, prioritize_live
from universal_led.soccer_screens import match_screen


def payload(league, state, home, away, clock=None, period=None):
    status = {"type": {"name": state}}
    if clock is not None:
        status["displayClock"] = clock
    if period is not None:
        status["period"] = period
    return {"events": [{
        "id": league + "-match",
        "status": status,
        "competitions": [{"competitors": [
            {"homeAway": "home", "team": {"abbreviation": home}, "score": "1"},
            {"homeAway": "away", "team": {"abbreviation": away}, "score": "0"},
        ]}],
    }]}


class SoccerReleaseIntegrationTests(unittest.TestCase):
    def test_both_leagues_live_and_favorites_select_correctly(self):
        mls, = parse_scoreboard(payload("MLS", "STATUS_IN_PROGRESS", "ATL", "MIA", "45'+1'", 1), "MLS")
        nwsl, = parse_scoreboard(payload("NWSL", "STATUS_IN_PROGRESS", "POR", "NJ", "67'", 2), "NWSL")
        games = prioritize_live((mls, nwsl))
        self.assertEqual(len(games), 2)
        self.assertEqual(eligible_matches(games, favorites=["POR"], mode="favorites"), (nwsl,))
        self.assertEqual(match_screen(mls).footer, "1H 45+1'")
        self.assertEqual(match_screen(nwsl).footer, "2H 67'")

    def test_halftime_stays_live_and_displays_ht(self):
        halftime, = parse_scoreboard(payload("MLS", "STATUS_HALFTIME", "ATL", "MIA", "45'", 1), "MLS")
        scheduled, = parse_scoreboard(payload("NWSL", "STATUS_SCHEDULED", "POR", "NJ"), "NWSL")
        self.assertEqual(prioritize_live((scheduled, halftime)), (halftime,))
        self.assertEqual(match_screen(halftime).footer, "HT")

    def test_final_and_scheduled_remain_when_nothing_live(self):
        final, = parse_scoreboard(payload("MLS", "STATUS_FINAL", "ATL", "MIA"), "MLS")
        scheduled, = parse_scoreboard(payload("NWSL", "STATUS_SCHEDULED", "POR", "NJ"), "NWSL")
        self.assertEqual(prioritize_live((final, scheduled)), (final, scheduled))
        self.assertEqual(match_screen(final).footer, "FINAL")
        self.assertEqual(match_screen(scheduled).footer, "PRE")


if __name__ == "__main__":
    unittest.main()
