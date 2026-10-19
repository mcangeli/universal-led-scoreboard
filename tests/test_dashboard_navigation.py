"""Navigation accessibility and page-selection regression tests."""
import unittest
from universal_led import configurator


class DashboardNavigationTests(unittest.TestCase):
    def test_every_sidebar_destination_has_a_page(self):
        import re
        html=configurator.HTML
        pages=set(re.findall(r'<(?:section|div)[^>]*\bdata-page="([a-z-]+)"',html))
        destinations=set(re.findall(r'class="nav-item"[^>]*onclick="showPage\(\'([^\']+)\'\)"',html))
        self.assertTrue(destinations)
        self.assertEqual(destinations,pages)

    def test_navigation_exposes_current_page_to_assistive_technology(self):
        html=configurator.HTML
        self.assertIn("button.setAttribute('aria-current','page')",html)
        self.assertIn("button.removeAttribute('aria-current')",html)
        self.assertIn("button.classList.toggle('active',active)",html)

    def test_unknown_page_does_not_hide_all_sections(self):
        html=configurator.HTML
        self.assertIn("if(!document.querySelector('[data-page=",html)
        self.assertIn("return;document.querySelectorAll('.nav-item')",html)


if __name__=='__main__':
    unittest.main()
