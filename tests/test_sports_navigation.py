"""Sports configuration navigation contract tests."""
import unittest
from universal_led import configurator


class SportsNavigationTests(unittest.TestCase):
    def test_rotation_entries_open_corresponding_sport(self):
        html=configurator.HTML
        self.assertIn("node.addEventListener('click',()=>selectSport(name))",html)
        self.assertIn("node.setAttribute('aria-label','Configure '",html)
        self.assertIn("node.type='button'",html)

    def test_invalid_sport_selection_is_ignored(self):
        self.assertIn("if(!Array.from(picker.options).some(option=>option.value===name))return",configurator.HTML)

    def test_invalid_sports_view_is_ignored(self):
        self.assertIn("if(!['overview','configure','rotation'].includes(view))return",configurator.HTML)


if __name__=='__main__':
    unittest.main()
