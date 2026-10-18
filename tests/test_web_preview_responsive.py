"""Mobile board view must keep the entire 64x32 canvas visible."""
import unittest
from universal_led.web_preview import HTML


class BoardPreviewResponsiveTests(unittest.TestCase):
    def test_canvas_scales_with_available_body_width(self):
        self.assertIn('name="viewport"', HTML)
        self.assertIn('box-sizing:border-box', HTML)
        self.assertIn('canvas{display:block;width:100%;max-width:896px;height:auto', HTML)
        self.assertIn('aspect-ratio:2/1', HTML)
        self.assertNotIn('width:min(96vw,896px)', HTML)


if __name__ == "__main__":
    unittest.main()
