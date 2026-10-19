"""Sports settings unsaved-change feedback regression coverage."""
import unittest
from universal_led import configurator


class SportsSaveFeedbackTests(unittest.TestCase):
    def test_sport_form_edits_report_unsaved_changes(self):
        html=configurator.HTML
        self.assertIn("event.target.closest('#sports-configure')",html)
        self.assertIn("sportsSettingsDirty=true",html)
        self.assertIn('Unsaved sport settings changes',html)
        self.assertIn("addEventListener('input',markSportsSettingsDirty)",html)
        self.assertIn("addEventListener('change',markSportsSettingsDirty)",html)

    def test_successful_save_clears_unsaved_message(self):
        html=configurator.HTML
        self.assertIn("sportsSettingsDirty=false;",html)
        self.assertIn("if(!response.ok)throw Error('Server rejected sport settings",html)


if __name__=='__main__':
    unittest.main()
