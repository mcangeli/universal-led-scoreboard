"""Guard the read-only multisport dashboard contract."""
import unittest
from universal_led import configurator


class DashboardOverviewContractTests(unittest.TestCase):
    def test_read_only_overview_has_all_eight_sports(self):
        html=configurator.HTML
        self.assertIn('id="dashboard-sports"',html)
        self.assertIn('id="dashboard-sports-summary"',html)
        self.assertIn('data-page="dashboard"',html)
        self.assertIn('Read-only configuration summary',html)
        self.assertIn('const sportGrid=',html)

    def test_live_scheduler_state_is_shown_without_changing_rotation(self):
        html=configurator.HTML
        self.assertIn('rotation.selected_sport===sport.id',html)
        self.assertIn('rotation.live_sports.includes(sport.id)',html)
        self.assertIn('Currently selected',html)
        self.assertIn('Live game available',html)
        self.assertIn('Live games first',html)

    def test_feed_health_handles_stale_error_and_disabled(self):
        html=configurator.HTML
        self.assertIn('Math.max(300,3*sport.refresh_seconds)',html)
        self.assertIn("'Not monitored'",html)
        self.assertIn("'Stale'",html)
        self.assertIn("'Error'",html)
        self.assertIn("'Healthy'",html)
        self.assertIn('sport.feed_last_success==null',html)

    def test_overview_uses_status_api_and_safe_dom_updates(self):
        html=configurator.HTML
        self.assertIn("fetch('/api/status'",html)
        self.assertIn('sportGrid.replaceChildren()',html)
        self.assertIn('detail.textContent=activity',html)
        self.assertIn('overview.textContent=enabled',html)


if __name__=='__main__':
    unittest.main()
