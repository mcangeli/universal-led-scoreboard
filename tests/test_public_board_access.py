"""Public board routes remain readable without opening privileged APIs."""
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen

from universal_led.configurator import make_handler
from universal_led.display import Framebuffer


class PublicBoardTests(unittest.TestCase):
    def test_anonymous_board_and_frame_but_not_settings(self):
        with tempfile.TemporaryDirectory() as root:
            frame = Framebuffer(64, 32)
            handler = make_handler(root, "test-token", board_provider=lambda: frame)
            # Silence only the expected access log lines from this test server.
            # Keep real HTTP responses and authorization assertions unchanged.
            with patch.object(handler, "log_message"):
                with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
                    thread = threading.Thread(target=server.serve_forever, daemon=True)
                    thread.start()
                    try:
                        base = "http://127.0.0.1:%s" % server.server_port
                        with urlopen(base + "/board", timeout=3) as response:
                            self.assertEqual(response.status, 200)
                            self.assertIn(b"/frame.json", response.read())
                        with urlopen(base + "/frame.json", timeout=3) as response:
                            data = json.load(response)
                            self.assertEqual((data["width"], data["height"]), (64, 32))
                            self.assertEqual(len(data["pixels"]), 64 * 32)
                        for path in ("/api/settings", "/api/config", "/api/matrix-settings"):
                            with self.assertRaises(HTTPError) as error:
                                urlopen(base + path, timeout=3)
                            self.assertEqual(error.exception.code, 401)
                    finally:
                        server.shutdown()
                        thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
