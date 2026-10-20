# v0.9.0 roadmap: Plugin architecture and extensibility

**Status:** architecture/design phase on `feature/0.9.0-dynamic-team-registry`. No plugin runtime or installer is implemented by this document.

## Goal
Make ULS expandable without core modifications for each new screen, data provider, or dashboard setup page. Preserve reliable 64×32 rendering, live-game priority, and existing system services.

## First: evaluate Bullpen and prior configurator
- Audit MLB-LED-Scoreboard Bullpen's lifecycle, rendering contract, configuration and packaging; compare it with ULS runtime/rotation boundaries.
- Review the earlier MLB Scoreboard Configurator's plugin repository editor, install/update/uninstall workflow, progress feedback and configuration cleanup.
- Record reusable patterns, gaps and reasons for choosing a native ULS interface; do not assume Bullpen plugins can run unchanged.

## Proposed architecture (subject to code audit)
1. **Versioned manifest and SDK:** plugin ID, version, ULS compatibility range, entry points, declared capabilities, settings schema, dependencies and permissions. Provide a starter template, developer docs and a local validation command.
2. **Screens:** registration API for 64×32 frame renderers, supported screen metadata, refresh lifecycle, rotation eligibility and priority, including live-game restrictions. Rendering must remain responsive; network I/O belongs in cached/background provider workers.
3. **Dashboard extensions:** automatically generated configuration forms from a validated schema; optional namespaced setup/information/status pages using supported components. No arbitrary plugin HTML/JavaScript injected into the privileged dashboard by default.
4. **Provider extensions:** cached background feeds, league/team discovery and stable provider-qualified IDs; migrate favorites safely and preserve unresolved favorites and season-scoped memberships.
5. **Catalogs:** default curated plugin index, add/remove custom GitHub-backed indexes, and explicit direct GitHub repository installation. Display source, publisher, version, compatibility and requested permissions before installing.
6. **Lifecycle:** browse, install, enable/disable, configure, update, rollback and uninstall via dashboard with persistent progress logs. Separate plugin settings/data from executable packages. Default uninstall preserves data or offers explicit cleanup.
7. **Security:** treat third-party plugins as executable code. Require explicit admin confirmation and a trust warning for custom sources; pin immutable commit/release refs and verify hashes where available. Restrict installation helpers and filesystem access; define isolation model before enabling untrusted code. Dependency installation must not alter the system Python environment.
8. **Reliability:** transactional install/update, health checks, recovery after interrupted operations, and disabling a broken plugin without stopping core ULS. Test physical and emulator rendering parity.

## Phased delivery
- **0.9.0-A:** code and Bullpen comparison, architecture decision record, legacy script dependency audit and README cleanup.
- **0.9.0-B:** plugin manifest, registry, discovery and sample screen plugin; emulator and physical-board tests.
- **0.9.0-C:** schema-driven dashboard forms, plugin pages and namespaced routes.
- **0.9.0-D:** catalogs, GitHub source registration, safe install/update/rollback/uninstall and progress feedback.
- **0.9.0-E:** provider/team registry integration and favorites migration.
- **0.9.0-F:** integration tests, compatibility/security review and production release gates.

## Acceptance criteria
- A documented external sample plugin installs from a GitHub source and adds a screen without editing ULS core.
- Its settings and information are accessible in the dashboard, and settings persist through core and plugin updates.
- Custom catalogs can be added, edited and removed; plugins can be installed, updated, disabled and uninstalled from the dashboard.
- Invalid or incompatible plugins are rejected before modifying the installation; failed updates preserve or restore the last working plugin.
- A plugin failure cannot take down the entire scoreboard; core services and existing screens remain usable.
- Existing favorites survive stable-ID-preserving renames; new provider teams become selectable; promotion/relegation does not destroy historical identity.
- Documentation clearly distinguishes trusted catalog entries from arbitrary third-party executable code and records redistribution/licensing constraints.

## Release discipline
Develop and test on Pi 5 first; keep production Pi 3 on `main` until approved. No claims of sandbox isolation or plugin security without implementation and verification.

## Initial architecture findings (October 20, 2026)

- Bullpen's documented contract uses Python package entry points under `bullpen.mlbled.plugin`, returning configuration, data and renderer classes. Its renderer produces one frame per call, with optional eligibility/reset hooks. This separation is worth preserving conceptually, but its update method may be called many times per second, so ULS should keep provider I/O in scheduled background workers.
- Bullpen's published documentation does not itself provide ULS-style dashboard page registration, schema-driven forms, GitHub catalog editing or transactional lifecycle management. Those are first-class ULS requirements, not presumed Bullpen compatibility.
- Removed obsolete user-level `scripts/install.sh` and staged `scripts/stage-system-services.sh` / `scripts/cutover-to-system.sh` from the v0.9 development branch. These targeted a different service layout from supported `scripts/install-system.sh`. Regression testing and reference audit remain required before treating cleanup as accepted.
