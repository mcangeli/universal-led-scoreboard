# Preview 12: native web configurator foundation

This preview starts the native configurator, borrowing **ideas** from the older
`mcangeli/mlb-scoreboard-configurator` project rather than installing its
Bullpen-specific implementation.

Features:
- Native web UI with team and global color pickers
- 64x32 preview using the shared MLB renderer
- Validated JSON saves, atomic file replacement, timestamped backups
- Persistent override files under `~/.config/universal-led-scoreboard`
- Local-only binding for initial safety

## Raspberry Pi

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.configurator --port 8080
```

Open `http://127.0.0.1:8080` **on the Pi itself**, or use an SSH tunnel
from your computer:

```sh
ssh -L 8080:127.0.0.1:8080 pi@YOUR_PI_IP
```

Then open `http://127.0.0.1:8080` on your computer.

The browser editor shows the complete effective palette, and saves it as
overrides. The existing Preview 11 CLI does not automatically read the
configurator directory. To test saved colors with Preview 11, use:

```sh
python3 -m universal_led.preview11 --host 0.0.0.0 --port 8765 --team ATL --mode fallback \
  --team-colors ~/.config/universal-led-scoreboard/teams.json \
  --scoreboard-colors ~/.config/universal-led-scoreboard/scoreboard.json
```

Preview 12 is **not a production administration portal**. It intentionally
rejects non-loopback binds. Its session token is not user authentication.
A later preview will add authentication, an explicit LAN access policy,
configuration versioning, and safe service integration.

The live browser preview currently uses a single selected MLB game; sport,
rotation and Wi-Fi/service controls are not yet implemented.
