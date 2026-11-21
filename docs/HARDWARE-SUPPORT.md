# Hardware and operating-system support policy

**Raspberry Pi OS Trixie 64-bit is the supported operating system for current ULS releases.** The system installer rejects Bookworm and non-64-bit installations.

The Raspberry Pi 5 is the development reference device, and the Raspberry Pi 3 is an actively used physical scoreboard. Browser/emulator mode has been exercised on the Pi 5. A complete clean-image physical installation remains a separate validation requirement.

| Board | Trixie 64-bit | Physical matrix |
| --- | --- | --- |
| Pi Zero 2 W | Target, performance unverified | Not validated |
| Pi 3 | Existing deployment verified | Physical scoreboard operated and updates tested; not a clean-image certification |
| Pi 4 | Target, unverified | Not validated |
| Pi 5 | Development and emulator installation tested | Existing physical setup exercised; clean-image physical installation pending |

These entries are **not hardware certification**. Pi 5 GPIO handling and driver support differ from earlier Pi models.

## Display backend contract

- Physical output and browser preview consume the same 64×32 framebuffer.
- A missing HAT or matrix must not prevent emulator operation.
- An unsupported hardware combination must fail clearly and leave configuration accessible.
- Brightness, mapping, and GPIO slowdown must be verified for the actual HAT and panel.
- Physical output requires a suitable external power supply.

## Validation

Use a separate clean boot card. Confirm install, web login, Wi-Fi recovery, services after reboot, physical splash, frame freshness, rotation, network-loss handling, and updates. Verify that the installer rejects unsupported OS releases. Record tested OS, Pi model, driver revision, HAT mapping, and results before claiming compatibility.
