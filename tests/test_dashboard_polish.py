"""v0.4.5 Preview 1 dashboard presentation regression checks."""
import unittest
from universal_led.configurator import HTML, LOGIN_HTML


class DashboardPolishTests(unittest.TestCase):
    def test_dashboard_data_hooks_remain_available(self):
        for element_id in ('summary', 'current-game', 'feed-indicator',
                           'feed-status', 'last-refresh', 'restart-scoreboard',
                           'restart-status'):
            with self.subTest(element_id=element_id):
                self.assertIn('id="' + element_id + '"', HTML)

    def test_restart_handler_preserved(self):
        self.assertIn('onclick="restartScoreboard()"', HTML)

    def test_dashboard_has_two_level_layout(self):
        self.assertIn('dashboard-tile-primary', HTML)
        self.assertIn('dashboard-actions', HTML)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))', HTML)
        self.assertIn('@media(max-width:680px)', HTML)

    def test_board_link_is_safe_and_unique(self):
        self.assertEqual(HTML.count('href="/board"'), 1)
        self.assertIn('href="/board" target="_blank" rel="noopener"', HTML)

    def test_dashboard_css_is_not_on_login(self):
        self.assertNotIn('/* v0.4.5 Preview 1:', LOGIN_HTML)
        self.assertIn('/* v0.4.5 Preview 1:', HTML)


if __name__ == '__main__':
    unittest.main()
