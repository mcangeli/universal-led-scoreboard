# Hardware and operating-system support policy

**Raspberry Pi OS Trixie 64-bit is the minimum supported operating system for v0.1.0.** Bookworm is out of scope and will not be tested or supported.

The Raspberry Pi 5 with a physical 64×32 HUB75 matrix is the active development and manually tested reference setup. A clean-image installation is pending.

| Board | Trixie 64-bit | Physical matrix |
| --- | --- | --- |
| Pi Zero 2 W | Target, performance unverified | Not validated |
| Pi 3 | Planned production validation | Not validated |
| Pi 4 | Target, unverified | Not validated |
| Pi 5 | Active development, existing installation tested | Working on development setup; clean installation pending |

These entries are **not hardware certification**. Pi 5 GPIO handling and driver support differ from earlier Pi models.

## Display backend contract

- Physical output and browser preview consume the same 64×32 framebuffer.
- A missing HAT or matrix must not prevent emulator operation.
- An unsupported hardware combination must fail clearly and leave configuration accessible.
- Brightness, mapping, and GPIO slowdown must be verified for the actual HAT and panel.
- Physical output requires a suitable external power supply.

## Validation

Use a separate clean boot card. Confirm install, web login, Wi-Fi recovery, services after reboot, physical splash, frame freshness, rotation, network-loss handling, and updates. Reject unsupported OS releases during the future clean-install bootstrap. Record tested OS, Pi model, driver revision, HAT mapping, and results before claiming compatibility.
