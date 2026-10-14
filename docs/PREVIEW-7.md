# Preview 7: background MLB updates and selection

Preview 7 moves MLB network calls off the HTTP preview request path. A daemon worker fetches schedule/linescore information and publishes cached game snapshots. Browser frame requests never initiate an API call.

## Run

```sh
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview7 --host 0.0.0.0 --port 8765 --team ATL --mode fallback
```

Visit `http://<pi-ip>:8765` from your LAN. Stop the previous preview process first.

Selection modes:
- `favorite`: show only the selected team's game; splash when none.
- `fallback` (default): prefer selected team's game; if none, cycle all games.
- `all`: cycle all games.

Options: `--date YYYY-MM-DD`, `--seconds 12`, `--refresh 60`.

If the initial request fails, the splash remains until a successful refresh. If a later refresh fails, the cached last-known game information is retained. The browser preview is unauthenticated and must not be exposed to the public internet.

Limitations: Still uses the Preview 5 refined layout, not upstream MLB Classic visual parity. Pregame and final layouts are still minimal. Worker refresh is interval-based and uses the existing eight-second API timeout. This is a development preview, not a service-managed production deployment.
