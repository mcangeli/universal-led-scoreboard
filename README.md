# Universal LED Scoreboard

Universal LED Scoreboard turns a Raspberry Pi and a compact RGB LED matrix into a configurable sports scoreboard, clock, weather display and news ticker. It combines classic score layouts with a browser-based configurator and a live 64×32 board preview, so most everyday changes do not require editing Python or JSON.

The project is being built as a multi-sport platform. **MLB, NHL, NBA and WNBA are implemented in v0.3.0.** NFL, MLS and EFL integrations are planned; they are not available scoreboard modes yet.

## What it does

- Displays MLB games with classic scoreboard, live matchup and previous-play views.
- Displays NHL games on 64×32 classic and visual layouts, including scheduled, live, intermission, overtime, shootout, final and postponed status indicators. Scheduled-game screens show team records when available.
- Displays NBA and WNBA scheduled, live and final games with pregame tipoff times and team records when supplied by the feed.
- Lets you select favorite MLB, NHL, NBA and WNBA teams, configure basketball and hockey game selection modes, and rotate enabled sports.
- Gives **live games involving favorite teams** priority over the normal screen rotation. Other games, clock, weather and news share the remaining rotation.
- Shows an optional clock with a timezone dropdown and 12/24-hour formats.
- Shows optional weather with colored pixel-art icons, temperature and forecast high/low. Choose Open-Meteo or OpenWeatherMap; OpenWeatherMap requires your own API key.
- Uses a shared universal news renderer for automatic MLB, NHL, NBA and WNBA headlines plus administrator-configured RSS/Atom sources; sources are interleaved rather than separated by sport.
- Provides a password-protected web configurator for sports, display colors, time/weather, news, Wi-Fi and board preview.
- Includes Wi-Fi connection and recovery functionality for supported Raspberry Pi installations.

The current screen layouts target a **64×32 RGB LED matrix**. You can use the browser emulator before connecting a physical matrix.

## Hardware and software

Development targets Raspberry Pi 5, with Raspberry Pi 3 as a production target. The hardware targets include Pi Zero 2 W, Pi 3, Pi 4 and Pi 5. **Raspberry Pi OS Trixie 64-bit is required**; Bookworm is not supported. The physical matrix and dashboard have been validated on the production Raspberry Pi 3; compatibility and performance on other models still require device-specific verification. Performance and hardware-driver behavior may vary by model.

For a physical board you need a compatible 64×32 RGB LED matrix, appropriate power supply, and an RGB matrix interface/HAT supported by the `rpi-rgb-led-matrix` driver. **The web emulator does not require matrix hardware.** Hardware wiring and service setup depend on the interface used.

## Installation status

**v0.3.0 adds NBA and WNBA to the validated MLB + NHL integration baseline.** The validated production installation runs two **system-level** services (`uls-web.service` and `uls-matrix.service`) from `/opt/uls/app`. The older `scripts/install.sh` installs a separate user-level preview service and **must not be used as the clean-install procedure for the current system layout**.

The system installer and CLI updater have been exercised on the Raspberry Pi installation. The v0.3.0 regression suite passed on the production Pi (752 tests, 15 skipped); the prior v0.2.0 baseline passed 717 tests with 15 skipped. Both system services started automatically after a full reboot during v0.2.0 verification. MLB, NHL and news rotation were visually confirmed on the physical matrix; NBA and WNBA screens were subsequently confirmed on the physical matrix for v0.3.0. Dashboard-initiated update installation remains a separate acceptance item. See [Installation and first-run guide](docs/INSTALLATION.md) and [Foundation release checklist](docs/FOUNDATION-RELEASE-CHECKLIST.md). Preserve a known-good boot card during hardware experiments.

### Updating an existing system installation

```bash
sudo ulsctl update
sudo ulsctl health
sudo ulsctl status
```

The updater validates the candidate test suite before installation, synchronizes the installed `ulsctl` command, and restarts both services. Configuration under `/etc/uls` and data under `/var/lib/uls` are preserved.

**Security:** The configurator uses HTTP on the LAN. Do not expose port 8080 to the public internet without HTTPS and appropriate access controls.

## Configure and use

After signing in, start with the MLB/NHL/NBA/WNBA team and sport rotation settings. Add your favorite team abbreviations (for example `ATL`), choose which games to display, and adjust rotation timing. When a favorite team's game is live, it takes display priority; otherwise eligible screens rotate.

Under **Display Settings → Time & Weather**, enable the clock, choose a timezone and time format, and optionally enable weather. Enter a city or US ZIP code and choose Fahrenheit or Celsius. Open-Meteo is the default provider; for OpenWeatherMap, select it and enter your API key in the dedicated field. The key is stored separately from ordinary settings. Weather requests run in the background and use a cache, so brief network interruptions need not blank the board.

Use the news settings to enable automatic MLB/NHL/NBA/WNBA headlines or add RSS/Atom feeds. Use the color controls to customize the scoreboard palette. **Open Board View** provides a convenient 64×32 preview without hardware.

## Service management and testing

For the current system installation:

```bash
sudo ulsctl status
sudo ulsctl restart
sudo ulsctl logs
sudo ulsctl health
```

The physical worker shows an approximately 30-second startup splash before normal frames. The health command verifies both services, the HTTP endpoint, and freshness of the published framebuffer. Clean-image installation and compatibility on additional Raspberry Pi models still need independent validation.

From a development checkout:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m universal_led --output splash.ppm
```

## Troubleshooting

- **Cannot sign in:** Check credentials and permissions in the deployed configuration directory (`/etc/uls` for the system installation).
- **Cannot open the configurator:** Check that the process or service is running, verify the Pi's IP address and confirm port 8080 is reachable from your LAN.
- **Weather does not appear:** Check that weather is enabled, the location is valid and the selected provider is configured. OpenWeatherMap requires a working API key. Background data may take a moment to load.
- **A screen is not appearing:** A live favorite-team game intentionally takes priority. Otherwise, check which screens are enabled and allow the rotation to advance.
- **Service does not start:** Run `sudo ulsctl logs` and `sudo ulsctl status` for the system installation.
- **Changes are not visible in the browser:** Refresh the page after restarting the service.

## v0.3.0 verification

- Production Raspberry Pi 3 on Raspberry Pi OS Trixie, 64×32 RGB LED matrix.
- Full regression suite: **752 tests, 15 skipped, no failures** (October 16, 2026).
- `uls-web.service` and `uls-matrix.service` enabled and running automatically after reboot.
- Configurator responding on port 8080; physical MLB/NHL and universal news rotation verified previously, with NBA/WNBA display and configuration confirmed for v0.3.0.
- NHL pregame records are visible on the board; NBA/WNBA pregame records appear when available from the feed.
- NHL score feed retains last good data on transient errors and uses the configured timezone for the game-day date.
- NBA/WNBA news controls and RSS parsing are covered by tests; live headline delivery remains to be checked.

See [Changelog](CHANGELOG.md) for release details.

## Project status and credits

The codebase is under active development. MLB, NHL, clock, weather, universal news and the native configurator are and NBA/WNBA are available in v0.3.0; NFL, MLS and EFL are future work. The original projects informing this effort include [MLB LED Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard), [NBA LED Scoreboard](https://github.com/m0ranwad/nba-led-scoreboard), [NFL LED Scoreboard](https://github.com/mikemountain/nfl-led-scoreboard), [MLS LED Scoreboard](https://github.com/alexanderthebadatcoding/mls-led-scoreboard) and [NHL LED Scoreboard](https://github.com/falkyre/nhl-led-scoreboard).

Review the licenses of any reused source code, images, logos and third-party feeds before redistribution. The MLB LED Scoreboard foundation is GPLv3.
