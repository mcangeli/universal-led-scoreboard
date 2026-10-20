"""Colors editor Cancel must restore NHL as well as MLB unsaved values."""
import unittest
from universal_led import configurator


class NHLColorCancelUITests(unittest.TestCase):
    def test_nhl_colors_have_saved_snapshot_and_dirty_tracking(self):
        html=configurator.HTML
        self.assertIn('let nhlColors=null,nhlSavedColors=null,nhlColorDefaults=null;',html)
        self.assertIn('nhlSavedColors=clone(nhlColors);markDirty();',html)
        self.assertIn('JSON.stringify(nhlColors)!==JSON.stringify(nhlSavedColors)',html)

    def test_cancel_restores_nhl_editor_and_marks_clean(self):
        html=configurator.HTML
        self.assertIn('nhlColors=clone(nhlSavedColors);showNHLColorEditor();',html)
        self.assertIn("Unsaved NHL color changes discarded.",html)

    def test_nhl_save_updates_saved_snapshot(self):
        html=configurator.HTML
        self.assertIn('nhlSavedColors[code]=clone(color);markDirty();',html)
        self.assertIn('nhlColors[code]=[...nhlColorDefaults[code]];showNHLColorEditor();markDirty();',html)


if __name__=='__main__':
    unittest.main()
