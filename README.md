# Universal LED Scoreboard

Universal LED Scoreboard turns a Raspberry Pi and a compact RGB LED matrix into a configurable sports scoreboard, clock, weather display and news ticker. It combines classic score layouts with a browser-based configurator and a live 64×32 board preview, so most everyday changes do not require editing Python or JSON.

The project is being built as a multi-sport platform. **MLB is the implemented sports module in this preview.** NBA, NFL, NHL, MLS and EFL integrations are planned; they should not be mistaken for available scoreboard modes yet.

## What it does

- Displays MLB games with classic scoreboard, live matchup and previous-play views.
- Lets you select favorite MLB teams and choose which games appear.
- Gives **live games involving favorite teams** priority over the normal screen rotation. Other games, clock, weather and news share the remaining rotation.
- Shows an optional clock with a timezone dropdown and 12/24-hour formats.
- Shows optional weather with colored pixel-art icons, temperature and forecast high/low. Choose Open-Meteo or OpenWeatherMap; OpenWeatherMap requires your own API key.
- Displays MLB news and configured RSS/Atom headlines.
- Provides a password-protected web configurator for sports, display colors, time/weather, news, Wi-Fi and board preview.
- Includes Wi-Fi connection and recovery functionality for supported Raspberry Pi installations.

The current screen layouts target a **64×32 RGB LED matrix**. You can use the browser emulator before connecting a physical matrix.

## Hardware and software

Development targets Raspberry Pi 5, with Raspberry Pi 3 as a production target. The intended compatibility range includes Pi Zero 2 W, Pi 3, Pi 4 and Pi 5 running Raspberry Pi OS Bookworm or Trixie. Performance and hardware-driver behavior may vary by model.

For a physical board you need a compatible 64×32 RGB LED matrix, appropriate power supply, and an RGB matrix interface/HAT supported by the `rpi-rgb-led-matrix` driver. **The web emulator does not require matrix hardware.** Hardware wiring and service setup depend on the interface used.

## Get started (browser emulator)

These steps run the Python application directly from a checkout. They are useful for first-time setup and testing before installing it as a background service.

1. Install Git and Python 3 on the Raspberry Pi.
2. Clone the project and check out the current preview branch:

   ```bash
   git clone https://github.com/mcangeli/universal-led-scoreboard.git
   cd universal-led-scoreboard
   git switch feature/0.1.0-core-foundation
   ```

3. Set the administrator password (minimum 12 characters):

   ```bash
   python3 -m universal_led.configurator --set-admin-password
   ```

4. Start the web configurator:

   ```bash
   python3 -m universal_led.configurator --host 0.0.0.0 --port 8080
   ```

5. On a device on the same network, open `http://<raspberry-pi-ip>:8080`, sign in, and use **Open Board View** to see the emulator. On the Pi itself, use `http://localhost:8080`.

The default configuration directory is `~/.config/universal-led-scoreboard`. To use a different directory, pass `--config-dir /path/to/config` to both the password-setup and server commands. Stop a foreground server with Ctrl+C.

**Security:** Port 8080 serves HTTP. Keep it on a trusted LAN; use HTTPS through a properly configured reverse proxy before making it accessible outside your network. Do not expose the configurator directly to the internet.

## Configure and use

After signing in, start with the MLB team and rotation settings. Add your favorite team abbreviations (for example `ATL`), choose which games to display, and adjust rotation timing. When a favorite team's game is live, it takes display priority; otherwise eligible screens rotate.

Under **Display Settings → Time & Weather**, enable the clock, choose a timezone and time format, and optionally enable weather. Enter a city or US ZIP code and choose Fahrenheit or Celsius. Open-Meteo is the default provider; for OpenWeatherMap, select it and enter your API key in the dedicated field. The key is stored separately from ordinary settings. Weather requests run in the background and use a cache, so brief network interruptions need not blank the board.

Use the news settings to enable official MLB headlines or add RSS/Atom feeds. Use the color controls to customize the scoreboard palette. **Open Board View** provides a convenient 64×32 preview without hardware.

## Run as a service

For an installation that already has the user-level systemd service configured:

```bash
systemctl --user status universal-led-scoreboard.service
systemctl --user restart universal-led-scoreboard.service
systemctl --user stop universal-led-scoreboard.service
systemctl --user start universal-led-scoreboard.service
journalctl --user -u universal-led-scoreboard.service -n 100 --no-pager
```

These commands **manage an existing service**; they do not install one. A new installation can use the foreground command above while hardware and service deployment are being configured.

## Updating and testing

From the preview checkout:

```bash
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests
```

If the tests pass and you run the systemd service, restart it to load the updated code. Keep local settings and API credentials out of Git. The project's release history and detailed changes are in [CHANGELOG.md](CHANGELOG.md), not this README.

To generate a splash-screen image without a matrix:

```bash
python3 -m universal_led --output splash.ppm
```

## Troubleshooting

- **Cannot sign in:** Run the administrator password setup command against the same configuration directory as the server.
- **Cannot open the configurator:** Check that the process or service is running, verify the Pi's IP address and confirm port 8080 is reachable from your LAN.
- **Weather does not appear:** Check that weather is enabled, the location is valid and the selected provider is configured. OpenWeatherMap requires a working API key. Background data may take a moment to load.
- **A screen is not appearing:** A live favorite-team game intentionally takes priority. Otherwise, check which screens are enabled and allow the rotation to advance.
- **Service does not start:** Inspect `journalctl --user -u universal-led-scoreboard.service -n 100 --no-pager`.
- **Changes are not visible in the browser:** Refresh the page after restarting the service.

## Project status and credits

The codebase is under active development. MLB, clock, weather, news and the native configurator are available in the current preview; other league integrations are future work. The original projects informing this effort include [MLB LED Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard), [NBA LED Scoreboard](https://github.com/m0ranwad/nba-led-scoreboard), [NFL LED Scoreboard](https://github.com/mikemountain/nfl-led-scoreboard), [MLS LED Scoreboard](https://github.com/alexanderthebadatcoding/mls-led-scoreboard) and [NHL LED Scoreboard](https://github.com/falkyre/nhl-led-scoreboard).

Review the licenses of any reused source code, images, logos and third-party feeds before redistribution. The MLB LED Scoreboard foundation is GPLv3.
