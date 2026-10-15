import unittest
from universal_led.configurator import HTML, LOGIN_HTML


class DashboardTilesTests(unittest.TestCase):
    def test_dashboard_preserves_status_targets(self):
        self.assertIn('class="dashboard-grid"',HTML)
        for identifier in ('summary','feed-status','current-game','last-refresh','feed-indicator'):
            self.assertEqual(HTML.count('id="'+identifier+'"'),1)

    def test_feed_indicator_uses_existing_status_response(self):
        self.assertIn("data.feed.error?'error'",HTML)
        self.assertIn("document.getElementById('feed-indicator').dataset.state='error'",HTML)

    def test_board_view_link_is_styled_and_unique(self):
        self.assertEqual(HTML.count('href="/board"'),1)
        self.assertIn('.sidebar-footer .board-button{',HTML)

    def test_dashboard_css_is_not_on_login_page(self):
        self.assertIn('.dashboard-grid{',HTML)
        self.assertNotIn('.dashboard-grid{',LOGIN_HTML)


if __name__=='__main__':
    unittest.main()
