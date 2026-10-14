# Preview 16: Dashboard diagnostics and Display settings

This release expands the running native configurator with:

- Dashboard: live MLB feed health, number of cached games, and current
  selected game (refreshed every ten seconds)
- Display: rotation mode, duration, and MLB data refresh interval
- Sports: favorite MLB team configuration, separate from display controls
- System: application uptime, backend type, and 64x32 emulator dimensions
- Existing Colors and Open Board View preserved

The dashboard is backed by the same feed and renderer as `/board`.
Systemd service actions and HUB75 hardware diagnostics are **not** implemented
yet. No claim of hardware connectivity is made.

## Raspberry Pi update

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
systemctl --user restart universal-led-scoreboard
systemctl --user status universal-led-scoreboard
```

Open `http://PI_IP:8080/` and `http://PI_IP:8080/board`.
Check the Dashboard and System tabs, then change rotation under Display.
Save, refresh, and verify that the selected settings persist and that
the board view continues to work. The application is intended for a trusted
LAN only until authentication is added.
