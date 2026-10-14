# Hardware and operating-system support policy

## Target combinations (not yet certified)

| Board | Raspberry Pi OS Bookworm | Raspberry Pi OS Trixie | Output |
| --- | --- | --- | --- |
| Pi Zero 2 W / WH | Target | Target | Emulator; physical HUB75 pending validation |
| Pi 3 | Target | Target | Emulator; physical HUB75 pending validation |
| Pi 4 | Target | Target | Emulator; physical HUB75 pending validation |
| Pi 5 | Target | Target | Emulator; physical HUB75 requires driver validation |

**Development hardware:** Raspberry Pi 5, Raspberry Pi OS Trixie, no HAT or matrix.

**Initial production hardware:** Raspberry Pi 3, Raspberry Pi OS Trixie.

These are product requirements, not claims of tested support. Validate OS/Python versions, CPU architectures, and driver builds per device. Pi 5 GPIO differs from older Pi models; never select a physical matrix driver solely by Raspberry Pi branding.

## Display backend contract

- Emulator and physical output must consume the same RGB framebuffer.
- Default to emulator mode on first install.
- A missing HAT/matrix must never prevent configuration or software-only preview.
- Unsupported hardware combinations must fail clearly and leave the web UI usable.
- Brightness, matrix dimensions, GPIO mapping and refresh parameters belong to backend configuration.

## Validation checklist

1. Install from a clean supported OS image.
2. Launch emulator without GPIO permissions.
3. Run automated foundation and plugin tests.
4. Confirm web configuration and boot-time service operation.
5. Verify Wi-Fi reconnect and recovery hotspot.
6. Test physical matrix only with supported hardware and explicit driver selection.
7. Record CPU/memory usage and update/restart behavior on each model.

## Status

No physical matrix drivers have been integrated or certified in this repository yet.
