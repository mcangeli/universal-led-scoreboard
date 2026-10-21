# Universal LED Scoreboard v0.9.0-rc.1 — release candidate notes

**Status: candidate prepared; tag and final acceptance pending.** This is not a stable release.

## Highlights

- Dynamic team registry foundation for league and team selection.
- Native external screen plugins with TOML manifests, configuration, enable/disable, and dashboard-driven GitHub install/update/removal.
- Commit-pinned plugin source review and transactional replacement, with validation before activation.
- Official plugin discovery catalog sourced from `mcangeli/uls-plugins`, including disk cache, manual refresh and bundled offline fallback.
- Idle rotation interleaves normal scoreboard content between enabled plugin screens; eligible live games retain priority over supplemental screens.
- Bundled Hello World example, developer documentation and plugin authoring reference.

## Compatibility and upgrade

- Raspberry Pi OS **Trixie 64-bit** on supported Pi Zero 2 W / 3 / 4 / 5 hardware; see the hardware support guide for physical matrix limitations.
- Dashboard updater validates candidate code before installing. Existing `/etc/uls` settings and `/var/lib/uls` state are preserved.
- External native plugins execute trusted Python code. The process boundary is **not** a security sandbox. Install only reviewed sources.
- Legacy Bullpen plugins are not compatible without conversion to native ULS plugins.
- The dashboard uses local-network HTTP by default. Do not expose it directly to the public internet.

## Validation so far

- Latest operator updater preflight on 2026-10-21 at `928fb8a`: **1,798 tests run, 15 skipped, no failures**; fast-forward installation successful; settings/state untouched by updater.
- Both Pi 3 and Pi 5 updater installations were confirmed clean on 2026-10-21; exact final test count for each device was not reported.
- Operator confirmed Pi 3 physical matrix, both browser previews, plugin rotation, official three-plugin catalog and favorite-team persistence through Pi 3 reboot. Corrected Standings help text was verified after a passing Pi 3 updater run.
- Automated tests cover remote catalog discovery, cached and offline fallback, malformed/oversized responses and preservation of a valid cache.

## Open acceptance and known limitations

- Automated plugin install/update/uninstall and failed-update rollback tests pass; manual destructive lifecycle smoke test remains open.
- Live-game preemption of supplemental plugins awaits an eligible live game; automated priority behavior is covered but final physical observation is pending.
- Portable backup/restore with 0.9.0 dynamic favorites, plugin setting persistence after restart, fresh physical install, and secret-handling diagnostics were not separately verified for this candidate. Treat these as unverified, not passed.
- Finalize candidate commit, tag `v0.9.0-rc.1`, and verify the tagged build before stable promotion. No Core feature additions during this release freeze.

## Intentionally not in Core 0.9.0

- Direct Google Calendar OAuth and recurring event support: planned external Daily Calendar plugin update. The current ICS calendar remains available.
- Automatic update-available notifications: deferred to Core v1.0.0. Updates remain administrator-approved.
- Native Magic Number / Green Monster conversions: separate external plugin work.

See [release checklist](release-0.9.0-checklist.md) and [changelog](../CHANGELOG.md) for detailed status.
