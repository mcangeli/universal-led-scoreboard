# HUB75 RGB matrix driver reference

**Upstream:** https://github.com/hzeller/rpi-rgb-led-matrix

This is the preferred physical HUB75 hardware backend for Universal LED Scoreboard, **not** an emulator dependency. The upstream README explicitly lists Raspberry Pi 1–5 support, including newly added Raspberry Pi 5 RP1 backends. Supported device/OS combinations still require our own hardware testing.

## Important upstream findings

- A 64x32 panel uses `--led-cols=64 --led-rows=32`.
- Raspberry Pi 5: `--led-rp1-pio=0` uses the RP1 RIO backend (default); `--led-rp1-pio=1` uses RP1 PIO, which the upstream README describes as lower CPU usage. These options only apply to Pi 5.
- Python bindings have been reworked (February 2026) to use scikit-build-core/CMake and the project can be installed from Git using pip. Validate installation in a project virtual environment before adding it to our installer.
- Expose panel dimensions, chain length, parallel chains, GPIO mapping, brightness, multiplexing, and slowdown settings through the web configurator.
- A supported HAT/adapter is recommended for safe level shifting. Follow upstream wiring documentation and power the panel appropriately.
- Python binding operations include `RGBMatrixOptions`, `RGBMatrix`, `SetImage` and offscreen frames with `SwapOnVSync`. Prefer a framebuffer-to-image transfer over repeated individual Python pixel calls where practical.
- The library is GPL-2.0-or-later; GPLv3 compatibility is explicitly documented upstream.

## Backend implementation contract

1. Use a driver interface that accepts our core framebuffer without coupling screens or plugins to the `rgbmatrix` module.
2. Import the native driver only if `backend=hub75`; emulator mode must run without the package, GPIO access, or a physical HAT.
3. Construct the driver once and avoid unbounded frame queues or duplicate initialization after restarts.
4. Select Pi 5-specific RP1 settings only on supported Pi 5 hardware and installed driver versions.
5. Provide explicit errors when the driver is missing, permissions are insufficient, or dimensions are incompatible.
6. Keep a headless emulator fallback for development on Pi 5 / Trixie without matrix hardware.
7. Before production certification, test Bookworm and Trixie separately on Pi Zero 2 W/WH, Pi 3, Pi 4 and Pi 5.

## Installer implications

Do **not** install or initialize the native driver by default on headless development devices. Offer an optional physical-HUB75 installation path with prerequisite checks and documented pin mapping. The scoreboard web service should remain unprivileged; isolate any elevated GPIO/display work into a narrowly scoped service.

## Follow-up

Upstream's README contains an older hardware-summary paragraph that says Pi 5 was not officially supported in November 2025, while its newer earlier section explicitly states Pi 5 support has now been added. Treat the latter as current project guidance, then validate against the actual pinned commit and target hardware.
