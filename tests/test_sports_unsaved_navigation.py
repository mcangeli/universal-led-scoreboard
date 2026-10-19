"""Guard navigation away from unsaved sports settings."""
import unittest
from universal_led import configurator


class SportsUnsavedNavigationTests(unittest.TestCase):
    def test_leaving_sports_page_prompts_when_dirty(self):
        html=configurator.HTML
        self.assertIn("name!=='sports'&&sportsSettingsDirty&&!confirm(",html)
        self.assertIn('Leave this page without saving?',html)

    def test_switching_sports_prompts_and_restores_picker_on_cancel(self):
        html=configurator.HTML
        self.assertIn('current.dataset.sportPanel!==name&&sportsSettingsDirty&&!confirm(',html)
        self.assertIn('picker.value=current.dataset.sportPanel;return;',html)
        self.assertIn('Your unsaved changes will remain in the form',html)


if __name__=='__main__':
    unittest.main()
