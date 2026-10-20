"""Countdown client validation mirrors important backend constraints."""
import unittest
from universal_led import configurator


class CountdownFormValidationTests(unittest.TestCase):
    def test_days_are_checked_before_save(self):
        html=configurator.HTML
        start=html.index('async function saveCountdown(){')
        end=html.index('async function loadClockSettings()',start)
        body=html[start:end]
        self.assertIn('!Number.isInteger(data.within_days)',body)
        self.assertIn('data.within_days<1||data.within_days>366',body)
        self.assertLess(body.index('Countdown days must'),body.index("fetch('/api/season-countdown'"))

    def test_enabled_automatic_mode_checks_sport_season_and_team(self):
        html=configurator.HTML
        self.assertIn("if(data.source==='automatic')",html)
        self.assertIn('Automatic countdown dates currently support MLB only.',html)
        self.assertIn('Automatic MLB countdown requires a four-digit season.',html)
        self.assertIn('Favorite-team automatic countdown requires a three-letter team code.',html)

    def test_manual_date_requires_timezone_and_season(self):
        html=configurator.HTML
        self.assertIn('Enabled manual countdown requires an opening date and timezone.',html)
        self.assertIn('Opening date must be a valid ISO timestamp with a timezone offset.',html)
        self.assertIn('A season is required when an opening date is set.',html)


if __name__=='__main__':
    unittest.main()
