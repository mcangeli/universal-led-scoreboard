# Installation and first-run experience

**Status:** design specification; the installer is not yet implemented.

## Goal

On a supported Raspberry Pi or similar SBC: install a supported OS, clone this repository, run `./install.sh`, open the web setup wizard, choose matrix hardware, select sports and teams, and start the scoreboard. Installation should not require editing JSON by hand.

## Planned guided workflow

1. Detect OS, architecture, display hardware and permissions; explain unsupported combinations.
2. Create an isolated Python virtual environment and install pinned dependencies.
3. Install a narrowly privileged system helper for network and service operations; keep the web application unprivileged.
4. Install and enable the scoreboard service, with safe recovery after interruption.
5. Configure Wi-Fi through the wizard; offer a fallback hotspot/captive portal when offline.
6. Select matrix dimensions, GPIO mapping, brightness, leagues, teams and display rotation.
7. Test the matrix or emulator, preview the startup splash and save settings.
8. Run a health check and provide update, backup, restore and uninstall instructions.

## Supported hardware policy

Raspberry Pi and 64x32 HUB75 matrices are the initial reference target. Other SBCs require a verified compatible matrix driver and will be documented separately. Never assume all Raspberry Pi GPIO drivers work on other SBCs.

## Documentation required for every milestone

- Installation and upgrade instructions
- Configuration reference with defaults
- User-facing change log and migration notes
- Common errors and troubleshooting
- Automated test instructions and a manual hardware test checklist
- Source/license attribution and third-party API requirements

## Acceptance criteria

A clean supported device can reach the first running scoreboard using the documented steps, without hand-editing configuration files. Failed installs and Wi-Fi configuration must be recoverable.
