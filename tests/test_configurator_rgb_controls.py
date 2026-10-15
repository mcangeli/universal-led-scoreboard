import unittest
from universal_led.configurator import HTML, LOGIN_HTML


class ConfiguratorRGBControlsTests(unittest.TestCase):
    def test_rgb_channels_and_bounds(self):
        self.assertIn("['Red','Green','Blue'].forEach",HTML)
        self.assertIn("slider.type='range'",HTML)
        self.assertIn("slider.min='0'",HTML)
        self.assertIn("slider.max='255'",HTML)

    def test_picker_slider_and_hex_are_synchronized(self):
        self.assertIn("picker.oninput=()=>update(rgb(picker.value))",HTML)
        self.assertIn("next[i]=Number(slider.value);update(next)",HTML)
        self.assertIn("hexValue.textContent=hex(next).toUpperCase()",HTML)
        self.assertIn("sliders.forEach((entry,i)=>",HTML)

    def test_changes_preserve_existing_preview_and_save(self):
        self.assertIn("selected={name,key};markDirty();draw()",HTML)
        self.assertIn("section('scoreboard');section('teams');markDirty();draw()",HTML)
        self.assertIn("body:JSON.stringify(state)",HTML)

    def test_styles_do_not_leak_into_login(self):
        self.assertIn(".color-channel input[type=range]",HTML)
        self.assertNotIn(".color-channel input[type=range]",LOGIN_HTML)


if __name__=='__main__':
    unittest.main()
