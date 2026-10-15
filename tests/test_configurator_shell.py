import unittest
from universal_led.configurator import HTML


class ConfiguratorShellTests(unittest.TestCase):
    def test_classic_shell_structure(self):
        self.assertIn('class="shell"',HTML)
        self.assertIn('<aside>',HTML)
        self.assertIn('aria-label="Configurator navigation"',HTML)
        self.assertIn('class="sidebar-footer"',HTML)

    def test_existing_pages_remain_available(self):
        for page in ('dashboard','sports','display','colors','wifi','system'):
            with self.subTest(page=page):
                self.assertIn('data-page="'+page+'"',HTML)
                self.assertIn("showPage('"+page+"')",HTML)

    def test_board_and_logout_controls_retained(self):
        self.assertIn('href="/board"',HTML)
        self.assertIn('onclick="logout()"',HTML)
        self.assertIn("function showPage(name)",HTML)


if __name__=='__main__':
    unittest.main()
