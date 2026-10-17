"""The browser preview must transmit renderer pixels without recoloring."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import urlopen
from unittest.mock import patch

from universal_led.colors import readable_on_black
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_visual import MLBVisualScreen, TEAM_COLORS
from universal_led.web_preview import make_handler


class PreviewColorParityTests(unittest.TestCase):
    def test_frame_json_preserves_contrast_adjusted_team_pixels(self):
        with patch.dict(TEAM_COLORS, {"ATL": (0, 0, 40)}):
            frame = MLBVisualScreen(BaseballGame(away="NYM", home="ATL")).render()
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(lambda: frame))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/frame.json", timeout=3) as response:
                payload = json.load(response)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
        self.assertEqual((payload["width"], payload["height"]), (64, 32))
        self.assertEqual(payload["pixels"], [list(pixel) for row in frame.pixels for pixel in row])
        self.assertIn(list(readable_on_black((0, 0, 40))), payload["pixels"])

    def test_bright_team_color_is_not_recolored(self):
        self.assertEqual(readable_on_black((240, 210, 90)), (240, 210, 90))


if __name__ == "__main__":
    unittest.main()
