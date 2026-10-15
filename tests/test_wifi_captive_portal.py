import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from universal_led.wifi_captive_portal import make_handler, PORTAL_URL, AP_ADDRESS

class CaptivePortalTests(unittest.TestCase):
    def test_fixed_hotspot_gateway(self):
        self.assertEqual(AP_ADDRESS, '10.42.0.1')
        self.assertEqual(PORTAL_URL, 'http://10.42.0.1:8080/login')

    def test_probe_receives_login_landing_not_success_204(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler())
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for path in ('/generate_204', '/hotspot-detect.html', '/connecttest.txt', '/'):
                connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
                connection.request('GET', path)
                response = connection.getresponse()
                body = response.read().decode()
                self.assertEqual(response.status, 200)
                self.assertIn(PORTAL_URL, body)
                self.assertNotIn('Success', body)
                connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)

if __name__ == '__main__':
    unittest.main()
