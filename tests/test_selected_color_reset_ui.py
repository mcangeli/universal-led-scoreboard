"""Selected color reset must not overwrite saved palette on failure."""
import unittest
from universal_led import configurator


class SelectedColorResetTests(unittest.TestCase):
    def test_reset_checks_default_response_and_missing_color(self):
        html=configurator.HTML
        body=html.split("document.getElementById('reset').onclick=async()=>{",1)[1].split('function invalidColorEntry(',1)[0]
        self.assertIn('if(!response.ok)throw Error',body)
        self.assertIn('if(!Array.isArray(color)||color.length!==3)',body)
        self.assertIn("status.textContent='Could not reset color: '+err.message",body)

    def test_reset_only_changes_editor_and_requires_save(self):
        html=configurator.HTML
        body=html.split("document.getElementById('reset').onclick=async()=>{",1)[1].split('function invalidColorEntry(',1)[0]
        self.assertIn('const target={...selected};',body)
        self.assertIn('state[target.name][target.key]=clone(color);',body)
        self.assertIn('Save to apply.',body)
        self.assertNotIn("method:'POST'",body)


if __name__=='__main__':
    unittest.main()
