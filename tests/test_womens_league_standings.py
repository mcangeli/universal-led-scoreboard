"""NWSL and WNBA standings regression tests."""
import copy
import unittest

from universal_led.nwsl_standings_feed import parse_nwsl_standings
from universal_led.wnba_standings_feed import parse_wnba_standings
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings
from universal_led.standings_screen import render_standings


def fixture():
    return {"standings": {"entries": [
        {"team": {"id": "101", "abbreviation": "ATL"},
         "stats": [{"name": name, "value": value} for name, value in {
             "wins": 12, "losses": 4, "ties": 3, "gamesPlayed": 19,
             "points": 39, "rank": 1, "gamesBehind": "0"}.items()]}
    ]}}


class WomensLeagueStandingsTests(unittest.TestCase):
    def test_nwsl_single_table(self):
        row, = parse_nwsl_standings(fixture())
        self.assertEqual((row.league, row.group, row.wins, row.draws, row.points),
                         ("NWSL", "NWSL", 12, 3, 39))
        self.assertIsNotNone(render_standings("NWSL", [row]))

    def test_wnba_single_table(self):
        row, = parse_wnba_standings(fixture())
        self.assertEqual((row.league, row.group, row.wins, row.losses, row.games_back),
                         ("WNBA", "WNBA", 12, 4, "0"))
        self.assertIsNotNone(render_standings("WNBA", [row]))

    def test_empty_provider_responses_fail(self):
        for parser in (parse_nwsl_standings, parse_wnba_standings):
            with self.subTest(parser=parser):
                with self.assertRaises(ValueError):
                    parser({})

    def test_standings_toggles_are_boolean(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings["standings"].update({"nwsl": True, "wnba": True})
        self.assertTrue(validate_settings(settings)["standings"]["nwsl"])
        settings["standings"]["wnba"] = "yes"
        with self.assertRaises(ValueError):
            validate_settings(settings)
