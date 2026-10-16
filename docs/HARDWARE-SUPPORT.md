# Hardware and operating-system support policy

The **Raspberry Pi 5 running Raspberry Pi OS Trixie with a physical 64×32 HUB75 matrix** is the active development and manually tested reference environment. The physical board and matrix worker are operating on that setup. A clean-image install is still pending.

| Board | Bookworm | Trixie | Physical matrix |
| --- | --- | --- | --- |
| Pi Zero 2 W | Target, unverified | Target, unverified | Not validated |
| Pi 3 | Target, unverified | Planned production validation | Not validated |
| Pi 4 | Target, unverified | Target, unverified | Not validated |
| Pi 5 | Target, unverified | Active development, existing install tested | Working on development setup; clean install pending |

These entries are **not hardware certification**. Pi 5 GPIO handling and driver support differ from earlier Pi models.

## Display backend contract

- Physical output and browser preview consume the same 64×32 framebuffer.
- A missing HAT or matrix must not prevent emulator operation.
- An unsupported hardware combination must fail clearly and leave configuration accessible.
- Brightness, mapping, and GPIO slowdown must be verified for the actual HAT and panel.
- Physical output requires a suitable external power supply.

## Validation

Use a separate clean boot card. Confirm install, web login, Wi-Fi recovery, services after reboot, physical splash, frame freshness, rotation, network-loss handling, and updates. Record tested OS, Pi model, driver revision, HAT mapping, and results before claiming compatibility.
