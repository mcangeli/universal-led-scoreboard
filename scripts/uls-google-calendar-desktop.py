"""Local desktop Google OAuth helper for ULS Daily Calendar.

Runs on the user's computer, not the Pi. Never sends tokens over the network
to the Pi: only writes a public-key-encrypted envelope for admin dashboard import.
Requires: pip install cryptography
"""
from __future__ import annotations

import argparse
import hashlib
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import urlencode, urlsplit, parse_qs
from urllib.request import Request, urlopen
import webbrowser

from universal_led.plugin_oauth_pairing_crypto import encrypt_for_public_key

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/calendar.readonly"


def validate_pairing(pairing):
    if not isinstance(pairing, dict) or set(pairing) != {"ticket", "public_key", "fingerprint", "expires_in"}:
        raise ValueError("Invalid pairing data")
    if not isinstance(pairing["ticket"], str) or len(pairing["ticket"]) < 32:
        raise ValueError("Invalid pairing ticket")
    pem = pairing["public_key"]
    if not isinstance(pem, str) or not pem.startswith("-----BEGIN PUBLIC KEY-----"):
        raise ValueError("Invalid pairing public key")
    fingerprint = hashlib.sha256(pem.encode("ascii")).hexdigest()
    if not secrets.compare_digest(fingerprint, pairing["fingerprint"]):
        raise ValueError("Pairing fingerprint mismatch")
    if pairing["expires_in"] != 300:
        raise ValueError("Unexpected pairing expiration")
    return fingerprint


def authorize(client_id, *, browser_open=webbrowser.open, opener=urlopen, timeout=180):
    if not isinstance(client_id, str) or not client_id.endswith(".apps.googleusercontent.com"):
        raise ValueError("Google Desktop OAuth client ID required")
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = __import__("base64").urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
    event = threading.Event()
    received = {}

    class Callback(BaseHTTPRequestHandler):
        def do_GET(self):
            if urlsplit(self.path).path != "/":
                self.send_error(404);return
            query = parse_qs(urlsplit(self.path).query)
            if query.get("state") != [state] or (not query.get("code") and not query.get("error")):
                self.send_error(400, "Invalid OAuth callback");return
            if not event.is_set():
                received.update(query)
                event.set()
            body = b"Google authorization received. Return to the ULS helper."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            pass

    with HTTPServer(("127.0.0.1", 0), Callback) as server:
        server.timeout = 1
        redirect = f"http://127.0.0.1:{server.server_port}/"
        url = GOOGLE_AUTH + "?" + urlencode({
            "client_id": client_id, "redirect_uri": redirect, "response_type": "code",
            "scope": SCOPE, "state": state, "code_challenge": challenge,
            "code_challenge_method": "S256", "access_type": "offline", "prompt": "consent"})
        print("Opening Google sign-in in your desktop browser.")
        browser_open(url)
        deadline = time.monotonic() + timeout
        while not event.is_set() and time.monotonic() < deadline:
            server.handle_request()
    if not event.is_set() or received.get("error"):
        raise ValueError("Google authorization cancelled or timed out")
    fields = urlencode({"client_id": client_id, "code": received["code"][0],
                        "code_verifier": verifier, "redirect_uri": redirect,
                        "grant_type": "authorization_code"}).encode("ascii")
    response = Request(GOOGLE_TOKEN, data=fields,
                       headers={"Content-Type": "application/x-www-form-urlencoded"})
    with opener(response, timeout=20) as stream:
        token = json.load(stream)
    if (not isinstance(token, dict) or
            not isinstance(token.get("access_token"), str) or
            not isinstance(token.get("refresh_token"), str)):
        raise ValueError("Google did not return offline credentials")
    expires_in = token.get("expires_in", 3600)
    if type(expires_in) is not int or not 0 < expires_in <= 86400:
        raise ValueError("Invalid Google token expiration")
    return {"access_token": token["access_token"], "refresh_token": token["refresh_token"],
            "client_id": client_id, "expires_at": int(time.time()) + expires_in}


def build_transfer(pairing, credentials):
    validate_pairing(pairing)
    return {"plugin_id": "daily-calendar", "provider": "google-calendar",
            "ticket": pairing["ticket"],
            "envelope": encrypt_for_public_key(pairing["public_key"], credentials)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Connect Google Calendar to ULS without a public Pi address")
    parser.add_argument("--client-id", required=True, help="Google Desktop OAuth client ID")
    parser.add_argument("--pairing", required=True, type=Path, help="Pairing JSON exported from ULS dashboard")
    parser.add_argument("--output", default=Path("uls-google-calendar-transfer.json"), type=Path)
    args = parser.parse_args(argv)
    pairing = json.loads(args.pairing.read_text(encoding="utf-8"))
    fingerprint = validate_pairing(pairing)
    print("Verify this SHA-256 fingerprint against your trusted Pi pairing screen:")
    print(fingerprint)
    if input("Does the fingerprint match? Type YES to continue: ").strip() != "YES":
        raise SystemExit("Pairing cancelled")
    credentials = authorize(args.client_id)
    transfer = build_transfer(pairing, credentials)
    args.output.write_text(json.dumps(transfer), encoding="utf-8")
    print(f"Encrypted transfer saved to {args.output}. Import it in the authenticated ULS dashboard.")
    print("Transfer expires five minutes after pairing started; do not share the transfer file.")


if __name__ == "__main__":
    main()
