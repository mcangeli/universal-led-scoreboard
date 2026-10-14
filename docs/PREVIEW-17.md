# Preview 17: MLB feed diagnostics and no-game behavior

This update improves the running configurator and board emulator:

- The Dashboard shows the feed's last attempted and last successful refresh.
- Feed state distinguishes startup, successful refresh, and errors.
- A successful response containing zero games is not considered a feed error.
- When there are no games selected, the board shows the splash screen instead
  of an invented NYM/ATL game.
- The Colors editor retains its sample-game fallback for offseason editing.

## Raspberry Pi verification

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
systemctl --user restart universal-led-scoreboard
```

Open `http://PI_IP:8080/` and `http://PI_IP:8080/board`.
Check the Dashboard's feed state and timestamps. If there are no MLB games,
the board should display the splash, not an invented matchup. The Colors
editor can still preview team colors using sample data.

Systemd controls, login authentication, and physical HUB75 output remain
future milestones.
