# Universal LED Scoreboard

Universal LED Scoreboard is a Raspberry Pi application for a **64×32 RGB LED matrix**, combining live sports scores, standings, a clock, weather and news in one configurable display. A password-protected web dashboard controls the board, while a browser preview works without physical matrix hardware.

## Features

- **Sports:** MLB, NHL, NBA, WNBA, NFL, MLS, NWSL and English football (Premier League, Championship, League One and League Two).
- **Games:** Scheduled, live and final score screens, league-appropriate clocks and game details, favorites and multi-sport rotation.
- **Priority:** Eligible live games take precedence over final/scheduled games and supplemental content. Final and scheduled games return when no eligible live games remain; standings display in idle slots when no eligible games remain.
- **Standings and alerts:** Football standings pages and scoring notifications, subject to provider data availability and configuration.
- **Extras:** Configurable news sources, time and weather, team colors, brightness and matrix settings.
- **Administration:** Browser dashboard, board preview, Wi-Fi management, service controls and preflight-tested software updates.

## Requirements

- Raspberry Pi Zero 2 W, Pi 3, Pi 4 or Pi 5; hardware and performance may vary by model.
- **Raspberry Pi OS Lite 64-bit Trixie**. Bookworm is not supported.
- For physical output: compatible 64×32 HUB75 RGB matrix, separate appropriate power supply and supported RGB matrix HAT/interface.
- Network access for sports data, weather, news and dashboard administration.

The browser-only emulator does not require a matrix or HAT. Do not connect or disconnect matrix wiring while powered.

## Installation

The supported system installation uses `scripts/install-system.sh` and installs `uls-web.service` and `uls-matrix.service`. The legacy `scripts/install.sh` creates a different user-level service and **is not** the supported clean-install path.

Start with a fresh Raspberry Pi OS Trixie image, configure SSH/networking and install Git:

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/mcangeli/universal-led-scoreboard.git
cd universal-led-scoreboard
```

For a physical 64×32 matrix with a compatible Adafruit HAT mapping:

```bash
bash scripts/install-system.sh --mode physical
```

For browser-only use:

```bash
bash scripts/install-system.sh --mode emulator
```

The installer prompts for an administrator password (minimum 12 characters), runs validation and provisions the services. Physical-mode defaults, including mapping and GPIO timing, must be checked against your hardware. For branch-specific testing, consult the installer options and [installation guide](docs/INSTALLATION.md); use a stable release for production deployments.

Open `http://<pi-host>:8080/` on your local network, then sign in with the administrator credentials created during setup.

## Configure and operate

1. In **Sports & Rotation**, enable leagues, choose favorites and game-selection mode, and set rotation intervals. For English football, choose divisions and clubs.
2. Under **Display Settings**, adjust colors, matrix settings, time, timezone and weather. OpenWeatherMap requires your own API key; Open-Meteo is also available.
3. Under **Content & News**, enable sports headlines and add optional RSS/Atom feeds.
4. Use **Open Board View** to inspect the 64×32 display in a browser.
5. Under **System → Software Updates**, check for updates and install a compatible branch or release. Candidate tests run before deployment; installed settings under `/etc/uls` and state under `/var/lib/uls` are preserved.

Live-game priority can suppress other pages while games are underway. When no eligible games remain, standings and optional news can rotate in idle slots.

### Service commands

```bash
sudo ulsctl status
sudo ulsctl health
sudo ulsctl logs
sudo ulsctl restart
```

The physical matrix shows a startup splash before normal frames. If the display appears blank immediately after boot, allow startup to finish and then check health and logs.

### Development tests

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m universal_led --output splash.ppm
```

## Troubleshooting and security

- **Dashboard unreachable:** Confirm the Pi's IP address, network connection and `uls-web.service` status. The default dashboard port is 8080.
- **No sports pages:** Check enabled leagues, favorites, game-selection mode and live-game priority.
- **No weather/news:** Verify the provider, location, feed configuration and network connectivity.
- **Matrix not displaying:** Check physical-matrix enablement, mapping, power and `sudo ulsctl logs`.
- **Update failed:** Read the updater's preflight log; a failed candidate validation should leave the running installation unchanged.

The web configurator uses HTTP on the local network. **Do not expose port 8080 directly to the internet** without HTTPS and appropriate access controls.

For more detailed setup and recovery instructions, see [Installation and first-run guide](docs/INSTALLATION.md), [Hardware support](docs/HARDWARE-SUPPORT.md), and [Dashboard updater](docs/DASHBOARD-UPDATER.md).

## Original projects and credits

Universal LED Scoreboard draws inspiration and foundational design ideas from these open-source scoreboard projects. They remain independent projects; their original authors deserve credit:

- [MLB LED Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard)
- [NBA LED Scoreboard](https://github.com/m0ranwad/nba-led-scoreboard)
- [NFL LED Scoreboard](https://github.com/mikemountain/nfl-led-scoreboard)
- [MLS LED Scoreboard](https://github.com/alexanderthebadatcoding/mls-led-scoreboard)
- [NHL LED Scoreboard](https://github.com/falkyre/nhl-led-scoreboard)
- [rpi-rgb-led-matrix hardware driver](https://github.com/hzeller/rpi-rgb-led-matrix)

See [LICENSE](LICENSE) for this repository's license. Reused code, artwork, logos and data feeds may have additional licensing or attribution requirements.

## Releases and history

Version-specific features, acceptance results, test counts, release status and historical notes belong in the [Changelog](CHANGELOG.md), not this README.
