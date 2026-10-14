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

## Development

Use `main` for integration and `feature/0.1.0-core-foundation` for initial implementation. Test rendering in an emulator before hardware deployment. League integrations are not yet implemented.

## Licensing

The MLB LED Scoreboard foundation is GPLv3. Review source and asset licensing before reusing code, images, logos or third-party data feeds.
