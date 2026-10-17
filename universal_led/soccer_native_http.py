"""Explicitly configured native league HTTP feeds.

No guessed production endpoints. URLs must be supplied after verifying each
league's API contract and access terms. Requests are bounded and JSON-only.
"""
import json
from datetime import date
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .soccer_native import parse_mls_matches, parse_nwsl_matches


def fetch_native_matches(league, day, *, url_template, timeout=5.0,
                         headers=None, opener=urlopen):
    if league not in ("MLS", "NWSL"):
        raise ValueError("Unsupported soccer league")
    if not isinstance(day, date):
        raise TypeError("day must be a date")
    if not isinstance(url_template, str) or not url_template:
        raise ValueError("Native endpoint must be configured")
    if type(timeout) not in (int, float) or not 0 < timeout <= 30:
        raise ValueError("Invalid native provider timeout")
    # Only the date token is interpolated; never interpolate arbitrary values.
    url = url_template.replace("{date}", day.strftime("%Y%m%d"))
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Native endpoint must use HTTPS without embedded credentials")
    request_headers = {"Accept": "application/json",
                       "User-Agent": "UniversalLEDScoreboard/0.5"}
    if headers is not None:
        if not isinstance(headers, dict) or any(
            not isinstance(k, str) or not isinstance(v, str) or
            "\r" in k + v or "\n" in k + v for k, v in headers.items()
        ):
            raise ValueError("Invalid native provider headers")
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    with opener(request, timeout=timeout) as response:
        payload = json.load(response)
    parser = parse_mls_matches if league == "MLS" else parse_nwsl_matches
    return parser(payload)


class NativeLeagueProvider:
    """Callable for SoccerProviderRouter.primary."""

    def __init__(self, league, *, url_template, timeout=5.0, headers=None,
                 opener=urlopen):
        self.league = league
        self.url_template = url_template
        self.timeout = timeout
        self.headers = headers
        self.opener = opener

    def __call__(self, day):
        return fetch_native_matches(
            self.league, day, url_template=self.url_template,
            timeout=self.timeout, headers=self.headers, opener=self.opener,
        )
