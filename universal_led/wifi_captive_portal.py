"""HTTP captive portal landing service, bound only to the setup AP address.

NetworkManager's shared-mode dnsmasq must resolve captive probes to this IP.
Authentication stays exclusively in the existing configurator.
"""
from __future__ import annotations
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

AP_ADDRESS = '10.42.0.1'
PORTAL_URL = 'http://10.42.0.1:8080/login'
PROBE_PATHS = frozenset(('/generate_204', '/gen_204', '/hotspot-detect.html',
                         '/library/test/success.html', '/connecttest.txt',
                         '/ncsi.txt', '/redirect', '/canonical.html'))

def make_handler(destination=PORTAL_URL):
    class PortalHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path.lower()
            if path == '/health':
                body = b'ok\n'
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            # Return HTML rather than expected 204/Success probes to trigger
            # the operating system's captive network assistant.
            body = ('<!doctype html><html lang="en"><head>'
                    '<meta name="viewport" content="width=device-width,initial-scale=1">'
                    '<title>Universal LED Scoreboard Setup</title>'
                    '</head><body><h1>Universal LED Scoreboard</h1>'
                    '<p>Sign in to configure Wi-Fi and your scoreboard.</p>'
                    '<p><a href="' + destination + '">Open scoreboard setup</a></p>'
                    '</body></html>').encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def do_HEAD(self):
            self.send_response(302)
            self.send_header('Location', destination)
            self.end_headers()
        def log_message(self, format, *args):
            # Suppress device probe URLs and identifiers in the journal.
            pass
    return PortalHandler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', default=AP_ADDRESS)
    parser.add_argument('--port', type=int, default=80)
    args = parser.parse_args()
    if args.bind != AP_ADDRESS:
        parser.error('Only the dedicated hotspot gateway address is allowed')
    with ThreadingHTTPServer((args.bind, args.port), make_handler()) as server:
        server.serve_forever()

if __name__ == '__main__':
    main()
