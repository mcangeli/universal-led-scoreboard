import unittest
from universal_led.configurator import HTML


class CompactMLBColorEditorTests(unittest.TestCase):
    def test_mlb_has_team_specific_controls(self):
        self.assertIn('id="mlb-save-color"', HTML)
        self.assertIn('id="mlb-reset-color"', HTML)
        self.assertIn('id="edit-team"', HTML)
        self.assertIn("fetch('/api/mlb-colors'", HTML)

    def test_nhl_controls_remain(self):
        self.assertIn('id="nhl-save-color"', HTML)
        self.assertIn('id="nhl-reset-color"', HTML)
        self.assertIn("fetch('/api/nhl-colors'", HTML)

    def test_existing_preview_and_full_palette_save_remain(self):
        self.assertIn("fetch('/api/frame'", HTML)
        self.assertIn("fetch('/api/config'", HTML)


if __name__ == '__main__':
    unittest.main()
