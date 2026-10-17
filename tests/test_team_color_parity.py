"""v0.4.5 color editor parity regression checks."""
import unittest
from universal_led.configurator import HTML, LOGIN_HTML


class TeamColorParityTests(unittest.TestCase):
    def test_both_sports_keep_edit_and_save_controls(self):
        for element_id in ('edit-team', 'teams', 'mlb-save-color', 'mlb-reset-color',
                           'nhl-edit-team', 'nhl-color-editor', 'nhl-save-color',
                           'nhl-reset-color'):
            with self.subTest(element_id=element_id):
                self.assertIn('id="' + element_id + '"', HTML)

    def test_nhl_uses_shared_color_editor_layout(self):
        start = HTML.index('function showNHLColorEditor(){')
        end = HTML.index('async function loadNHLColors()', start)
        body = HTML[start:end]
        for token in ('color-editor', 'color-name', 'color-hex',
                      'color-channels', 'color-channel', "input.type='range'",
                      "picker.type='color'"):
            with self.subTest(token=token):
                self.assertIn(token, body)

    def test_existing_nhl_api_still_used(self):
        self.assertIn("fetch('/api/nhl-colors'", HTML)
        self.assertIn("nhlColors[code]=next", HTML)

    def test_login_not_changed(self):
        self.assertNotIn('function showNHLColorEditor()', LOGIN_HTML)


if __name__ == '__main__':
    unittest.main()
