# Preview 8: MLB 64x32 visual improvements

Preview 8 adds a team-accent palette and separate delayed/postponed status labels while preserving Preview 7's live data worker and selection modes.

**This is not yet a faithful port of upstream MLB Classic.** Team accents are approximate RGB choices; no original logos or assets have been imported. Pregame screens do not yet show first pitch or probable pitchers. Postgame displays remain compact.

## Test on Pi

Stop the existing preview process.

```sh
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview8 --host 0.0.0.0 --port 8765 --team ATL --mode fallback
```

Open `http://<pi-ip>:8765` on a trusted LAN. You can use `--mode all`, `--date YYYY-MM-DD`, `--refresh 60`, and `--seconds 12`.

All screens remain native 64x32. The browser preview has no authentication and must not be exposed publicly.

## Remaining work

Faithful MLB Classic layout and typography, first pitch/probable pitchers, special status handling, richer postgame displays, plugin framework, and web configuration.
