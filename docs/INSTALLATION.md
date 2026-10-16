# Installation and first-run guide (v0.1.0 candidate)

**Important: the new clean system-service installer is experimental and has not yet been validated on a fresh image.** Do not wipe a working scoreboard or assume `scripts/install.sh` provisions the production layout. That script creates an older **user-level** `universal-led-scoreboard.service`. The current working installation uses **system-level** `uls-web.service` and `uls-matrix.service`.

## Before a clean-install test

1. Preserve the existing boot card/image. Use a **second microSD card** on the Raspberry Pi 5.
2. Record hardware mapping, brightness, and any driver-specific settings from the known-good device. Never publish administrator passwords, API keys, or Wi-Fi credentials.
3. Flash Raspberry Pi OS Lite 64-bit **Trixie** (required; Bookworm is unsupported) and configure SSH and networking using Raspberry Pi Imager.
4. Boot and verify SSH, network connectivity, system clock, and OS version.
5. Clone the candidate branch:

```bash
sudo apt update
sudo apt install -y git
git clone -b feature/0.1.0-core-foundation https://github.com/mcangeli/universal-led-scoreboard.git
cd universal-led-scoreboard
python3 --version
cat /etc/os-release
```

Run the new **experimental** system installer from the checkout as a regular sudo-enabled user. For a Pi with a physical 64×32 HUB75 panel and compatible Adafruit HAT mapping:

```bash
bash scripts/install-system.sh --mode physical
```

For browser-only testing without an LED matrix:

```bash
bash scripts/install-system.sh --mode emulator
```

The installer will prompt for an administrator password (minimum 12 characters), execute the tests, and enable system services. The physical mode compiles the RGB matrix driver and uses default mapping `adafruit-hat`, brightness `40`, GPIO slowdown `4`. These defaults are hardware-specific and must be checked before physical testing. Keep the panel's power supply disconnected while assembling wiring.

**Do not run the legacy `scripts/install.sh`** on this installation. The existing `scripts/stage-system-services.sh` and `scripts/cutover-to-system.sh` are **migration tools**: they require a previously migrated `/opt/uls/app`, `/etc/uls/admin.json`, and, for cutover, a running legacy service. They are not suitable for a fresh image.

## Known-good deployed layout (existing installations)

| Purpose | Path or service |
| --- | --- |
| Application | `/opt/uls/app` |
| Python environment | `/opt/uls/venv` |
| Settings and credentials | `/etc/uls` |
| Persistent state | `/var/lib/uls` |
| Published framebuffer | `/run/uls/live-frame.ppm` |
| Web service | `uls-web.service` |
| Physical display | `uls-matrix.service` |
| Management command | `/usr/local/bin/ulsctl` |
| Browser dashboard | `http://<pi-host>:8080/` |

Existing deployments can safely update and check health:

```bash
sudo ulsctl update
sudo ulsctl health
sudo ulsctl status
sudo ulsctl logs
```

The updater tests candidate code, fast-forwards the checked-out branch, synchronizes the installed management command, restarts both services, and checks the web endpoint. A failed update attempts rollback.

## Hardware and acceptance testing

The reference hardware is a 64×32 HUB75 RGB matrix attached to a Raspberry Pi 5 running Trixie. A compatible interface/HAT, separate matrix power supply, and supported `rpi-rgb-led-matrix` driver are required. Never connect or disconnect the panel while powered.

The fresh-install test must verify: installer completes without preexisting `/opt/uls` files; admin account setup; web login; board emulator; matrix driver and mapping; boot-time service startup; 30-second splash; live frame generation; Wi-Fi; dashboard restart; and safe update. Record the outcome in `docs/FOUNDATION-RELEASE-CHECKLIST.md`.

Pi 3 and other hardware remain separate compatibility validation targets. Bookworm is intentionally unsupported.

## Troubleshooting existing installations

```bash
sudo ulsctl status
sudo ulsctl logs
sudo ulsctl restart
sudo ulsctl health
```

If dashboard restart support is absent on an upgraded installation:

```bash
sudo bash /opt/uls/app/scripts/install-dashboard-restart-helper.sh
```

The web interface uses HTTP on the local network. Do not expose it publicly without TLS and appropriate access controls.
