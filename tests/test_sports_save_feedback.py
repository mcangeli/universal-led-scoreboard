"""Sports settings unsaved-change feedback regression coverage."""
import unittest
from universal_led import configurator


class SportsSaveFeedbackTests(unittest.TestCase):
    def test_sport_form_edits_compare_with_saved_snapshot(self):
        html = configurator.HTML
        self.assertIn("event.target.closest('#sports-configure')", html)
        self.assertIn("function sportsFormSnapshot()", html)
        self.assertIn("sportsFormSnapshot()!==savedSportsForm", html)
        self.assertIn("sportsSettingsDirty=savedSportsForm!==null", html)
        self.assertIn("sportsSettingsDirty?'Unsaved sport settings changes':''", html)
        self.assertIn("addEventListener('input',markSportsSettingsDirty)", html)
        self.assertIn("addEventListener('change',markSportsSettingsDirty)", html)

    def test_successful_save_refreshes_saved_snapshot(self):
        html = configurator.HTML
        self.assertIn("function resetSportsSettingsDirty()", html)
        self.assertIn("savedSportsForm=sportsFormSnapshot();", html)
        self.assertIn("sportsSettingsDirty=false;", html)
        self.assertIn("resetSportsSettingsDirty();", html)
        self.assertIn("if(!response.ok)throw Error('Server rejected sport settings", html)
        self.assertLess(
            html.index("if(!response.ok)throw Error('Server rejected sport settings"),
            html.index("  resetSportsSettingsDirty();\n  status.textContent='Sport settings saved.'"),
        )


if __name__ == '__main__':
    unittest.main()
