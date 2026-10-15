import unittest
from universal_led.configurator import HTML


class ColorEditorNavigationTests(unittest.TestCase):
    def test_palettes_have_separate_explanations(self):
        self.assertIn('General display text, accents, separators and status colors.',HTML)
        self.assertIn('All other team colors remain unchanged.',HTML)

    def test_team_editor_is_scoped_without_mutating_palette(self):
        self.assertIn('id="edit-team"',HTML)
        self.assertIn("name!=='teams'||key===document.getElementById('edit-team').value",HTML)
        self.assertIn("Object.keys(state.teams).sort()",HTML)

    def test_team_editor_and_preview_stay_in_sync(self):
        self.assertIn("editor.value=selectedTeam",HTML)
        self.assertIn("document.getElementById('edit-team').onchange",HTML)
        self.assertIn("document.getElementById('preview-team').value=selectedTeam",HTML)

    def test_color_controls_still_update_preview(self):
        self.assertIn("selected={name,key};markDirty();draw()",HTML)
        self.assertIn("body:JSON.stringify(state)",HTML)


if __name__=='__main__':
    unittest.main()
