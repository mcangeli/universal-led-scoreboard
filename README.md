# Universal LED Scoreboard

A modular, multi-sport Raspberry Pi LED scoreboard with classic league displays, a web configurator, and an extensible plugin system.

## Core principles

- Preserve each league's original scoreboard appearance as the default Classic theme.
- Use one display engine and shared screen scheduler, targeting 64x32 matrices first.
- Keep league data adapters separate from visual renderers.
- Provide a simple web setup wizard, Wi-Fi/hotspot recovery, team selection and live preview.
- Support safe, versioned plugins with installation, updates, diagnostics and rollback.
- Maintain compatibility with existing MLB Bullpen plugins where feasible.

## Source projects

- [MLB LED Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard)
- [NBA LED Scoreboard](https://github.com/m0ranwad/nba-led-scoreboard)
- [NFL LED Scoreboard](https://github.com/mikemountain/nfl-led-scoreboard)
- [MLS LED Scoreboard](https://github.com/alexanderthebadatcoding/mls-led-scoreboard)
- [NHL LED Scoreboard](https://github.com/falkyre/nhl-led-scoreboard)
- [NHL Pi Image](https://github.com/falkyre/nhl-led-scoreboard-img)
- [Our MLB Configurator](https://github.com/mcangeli/mlb-scoreboard-configurator)

## Roadmap

| Milestone | Scope |
| --- | --- |
| v0.1.x | Core architecture, plugin contract, emulator and MLB Classic |
| v0.2.x | Web configurator, onboarding, Wi-Fi and hotspot |
| v0.3.x | Plugin registry, management and Bullpen adapter |
| v0.4.x | NFL, NBA and NHL classic displays |
| v0.5.x | MLS and EFL, extensible European football |
| v0.6.x | Rotation profiles, themes, diagnostics and polish |
| v1.0.0 | Stable release and installation tooling |

## Current implementation (0.1.0 preview)

The MLB module, 64×32 emulator, native web configurator, Wi-Fi setup, news rotation, and independent clock/weather screens are implemented on `feature/0.1.0-core-foundation`. Weather supports Open-Meteo and optional OpenWeatherMap credentials. The shared scheduler gives exclusive display priority only to live games involving configured favorite teams; other content rotates normally. NBA, NFL, NHL, MLS, and EFL remain planned integrations, not completed displays.

## Development and validation

Use `main` for integration and `feature/0.1.0-core-foundation` for current preview development. On a Raspberry Pi checkout, run:

```bash
python3 -m unittest discover -s tests
```

The most recent user-validated baseline is 550 tests passing, 15 skipped. Run the full suite again after any release preparation changes. Test rendering in the emulator before hardware deployment.

The `0.1.0` version is still a preview until integration review, version finalization, and tagging are complete.

## Licensing

The MLB LED Scoreboard foundation is GPLv3. Review source and asset licensing before reusing code, images, logos or third-party data feeds.
