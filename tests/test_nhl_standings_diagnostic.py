import unittest
from unittest.mock import patch

from universal_led.nhl_standings_diagnostic import diagnose
from universal_led.standings import Standing


class NHLStandingsDiagnosticTests(unittest.TestCase):
    def test_valid_current_season_and_rows(self):
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        season = lambda _: [{"phase": "regular",
                             "start": (now-timedelta(days=1)).isoformat(),
                             "end": (now+timedelta(days=1)).isoformat()}]
        row = Standing(league="NHL", group="Atlantic", team_id="BOS",
                       abbreviation="BOS", played=2, wins=1, losses=1,
                       draws=0, points=2, rank=1)
        result = diagnose(season_fetcher=season, standings_fetcher=lambda _: [row])
        self.assertTrue(result["eligible"])
        self.assertEqual(result["groups"], {"Atlantic": 1})

    def test_calendar_failure_does_not_hide_feed_error(self):
        def failed(_):
            raise RuntimeError("calendar unavailable")
        result = diagnose(season_fetcher=failed, standings_fetcher=lambda _: [])
        self.assertEqual(result["season_phase"], "unknown")
        self.assertEqual(result["season_error"], "calendar unavailable")
        self.assertEqual(result["standings_rows"], 0)
        self.assertFalse(result["eligible"])


if __name__ == "__main__":
    unittest.main()
