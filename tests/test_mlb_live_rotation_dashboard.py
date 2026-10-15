import unittest
from universal_led.configurator import HTML


class LiveRotationDashboardTests(unittest.TestCase):
    def test_dashboard_has_live_rotation_fields(self):
        self.assertIn('id="live-classic"',HTML)
        self.assertIn('id="live-matchup"',HTML)
        self.assertIn('id="live-play-share"',HTML)

    def test_dashboard_loads_and_saves_percentages(self):
        self.assertIn("mlb.live_classic_percent",HTML)
        self.assertIn("mlb.live_matchup_percent",HTML)
        self.assertIn("function updateLiveShare()",HTML)

    def test_dashboard_prevents_invalid_allocation(self):
        self.assertIn("classic+matchup<=100",HTML)
        self.assertIn("if(!updateLiveShare())",HTML)


if __name__=='__main__':
    unittest.main()
