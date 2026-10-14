# Preview 15: run the configurator and board emulator together

One native server exposes:
- `http://PI_IP:8080/`: web configurator
- `http://PI_IP:8080/board`: read-only 64x32 live board emulator
- `http://PI_IP:8080/frame.json`: current scoreboard frame

Both pages share the same MLB background worker and settings. Saved colors
are loaded for each board frame, while saved MLB rotation and team settings
are applied immediately to the configurator's running renderer.

## Install as a systemd user service (Raspberry Pi)

First stop any manually running configurator on port 8080 (Ctrl+C).
Then:

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
bash scripts/install-user-service.sh
systemctl --user status universal-led-scoreboard.service
```

The installer uses your current checkout and Python 3, and writes the service
under `~/.config/systemd/user/`. It does not require root. The service starts
automatically when your user systemd manager starts. For startup without a
login session, an administrator can enable lingering separately using
`sudo loginctl enable-linger "$USER"`.

```sh
systemctl --user restart universal-led-scoreboard.service
systemctl --user stop universal-led-scoreboard.service
systemctl --user start universal-led-scoreboard.service
journalctl --user -u universal-led-scoreboard.service -f
```

Open both pages in separate browser tabs and save a new team color or
favorite team. The board should reflect the new settings on its next refresh.

Note: The board route is an emulator, not HUB75 hardware output. Port 8080
is unauthenticated and must remain on a trusted LAN.
