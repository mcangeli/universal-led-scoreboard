# v0.8.0 Unified Dashboard Release Checklist

**Status:** release-candidate exceptions accepted by user; feature branch **not merged or tagged**. Updated October 20, 2026.

This is the authoritative v0.8.0 acceptance checklist. Earlier version-specific checklists are historical records and do not automatically certify this release.

## Delivered in the candidate

- Unified read-only dashboard with sport and feed diagnostics, refresh timestamps, host/service/hardware summary, and current scheduler selection.
- Portable configuration backup download, selective import, hostname-based archive names and pre-restore recovery snapshots. Hardware, Wi-Fi and credentials are not portable.
- Content & News settings editing, source validation, saved/dirty tracking, navigation warnings, confirmed discard and failed-load handling.
- Live-game priority, scoring alerts, standings, final handoff and multi-sport rotation improvements carried forward from previous release candidates.
- Candidate validation before dashboard update, persistent progress logs and compatibility/branch checks.

## Verified evidence

- [x] User-confirmed Raspberry Pi updater preflight: **1,647 tests passed, 15 skipped** (October 20, 2026), installed commit `f765ff2bd9c8f04525ad7d334db2421efc4a10d0`; mandatory Node.js dashboard syntax check included.
- [x] Portable backup export and selective import tested; configuration restored and scoreboard services reloaded.
- [x] Configuration archive transferred from Pi 3 to Pi 5; differing settings updated as expected.
- [x] Export archive filename includes hostname; correction passed user checks.
- [x] Dashboard updater rejects failing candidate tests before modifying installed checkout (observed during development).
- [x] Dashboard navigation restored after JavaScript syntax regression; user confirmed responsive site. Installer now installs Node.js and preflight requires JavaScript parsing.
- [x] Dashboard Restart Services tested successfully by user on both Pi 3 physical and Pi 5 emulator installations (October 20, 2026). Worker now respects absent/disabled matrix service; regression tests added.
- [x] Dashboard authentication and session continuity manually verified on both Pis: refresh, page navigation, service restart, logout/login, and settings retained (October 20, 2026). Session expiry duration itself not manually elapsed.
- [x] Content & News manual persistence workflow passed on both Pi 3 and Pi 5: unsaved warning, cancel, discard, save, service restart, reload and restoration of original setting (October 20, 2026).
- [x] Pi 5 rollback helper structural regression checks passed (3 tests), web health passed, and working tree clean (October 20, 2026). This does not certify post-install failure recovery.
- [x] Pi 5 isolated post-checkout failure simulation passed alongside structural checks (4 tests total, October 20, 2026); web health OK and Git clean. Shell command doubles prevent changes to actual services or Git. This is automated rollback-path evidence, not an end-to-end live rollback.
- [x] Pi 5 persistent updater log and status inspected: `completed`, update `1435d4b` → `3ecdd15`, scoped dashboard/Wi-Fi helpers installed, sudoers checks passed, existing hotspot preserved, persistent settings reported untouched (October 20, 2026).
- [x] Pi 3 physical driver inventory: `rpi-rgb-led-matrix` commit `14464b3`, clean checkout, matrix enabled/active and frame 1 second old, web healthy (October 20, 2026).
- [x] Previous Pi 5 Trixie fresh-card **emulator** installation and reboot validated; this is not clean physical-install validation.
- [x] Prior user observations of EPL live/halftime/second-half/stoppage/final and Pi 3 multi-sport live priority are documented in the v0.7.0 checklist. These are prior acceptance evidence, not proof of every v0.8.0 provider/event combination.

## Outstanding release gates

- [ ] Audit redistribution provenance for any copied code, fonts, logos, graphics and bundled data; record upstream license and required notices for each. README credits alone do not establish license compliance.
- [x] Document the external sports/news/weather endpoints, relevant published provider restrictions, and user-discretion/change-without-notice disclaimer in [DATA-SOURCES.md](DATA-SOURCES.md), [THIRD-PARTY-ATTRIBUTION.md](THIRD-PARTY-ATTRIBUTION.md), and README (October 20, 2026). **This completes documentation, not permission clearance:** commercial use, redistribution rights, and specific provider API authorization remain unresolved.
- [ ] Verify a **fresh physical-mode Trixie installation**, RGB driver build, 64×32 output, HAT mapping, startup splash and saved matrix state after reboot. Use a spare card. This gate remains open by user choice; do not reinstall either working Pi to close it.
- [x] Pi 3 and Pi 5 operational smoke checks: Board View updating, enabled leagues/favorites retained, Wi-Fi scan shows nearby networks and identifies current connection (user confirmed October 20, 2026). Pi 5 persistent updater log/status also verified. No network change was performed.
- [ ] Confirm live-event-specific behaviors not yet physically observed; deterministic tests do not substitute for provider and hardware verification.
- [ ] Confirm post-deployment rollback/recovery behavior with a safe supervised plan; preflight rejection is not equivalent to tested post-install rollback. Existing isolated failure-injection tests are passing, but no real service-switch rollback has been observed.
- [x] Pi 5 full regression suite: **1,652 tests passed, 15 skipped** after release-identity fixture isolation fixes (October 20, 2026). Branch commit at time of run: `21c0f1fe2353a27a97613f9af57285d5d9254f5c` (user reported test count; commit inferred from latest pushed test fix, not independently reported from device). Re-run only if subsequent production or test code changes warrant it.
- [ ] Obtain explicit release approval **before** merging into main or tagging v0.8.0.

**Decision needed:** Whether the outstanding physical fresh-install and real rollback exercises are mandatory for v0.8.0 GA or will be accepted as documented limitations with a follow-up validation milestone. No approval has been assumed.

## Additional operator installation feedback

- [x] User reports that the recent v0.8.0 candidate version installs successfully (October 20, 2026). Installation method, device, exact installed commit and whether this was a fresh card were not specified; this is **not** evidence that the deferred fresh physical-mode Trixie installation gate is complete.

## Release-candidate exception acceptance (October 20, 2026)

**User decision:** Approved preparing and shipping a **v0.8.0 release candidate with documented limitations**. This is not approval to represent the build as fully validated general availability, nor explicit authorization to merge into `main` or create the final `v0.8.0` tag.

Accepted deferrals and exceptions:

- A clean physical-mode Raspberry Pi OS Trixie installation on a spare SD card, including RGB driver compilation, startup splash, HAT mapping and reboot persistence, has **not** been performed for this candidate. The existing Pi 3 physical installation and Pi 5 emulator are operational; do not reinstall them to close this gate.
- A real post-deployment failure/rollback has **not** been exercised on a running installation. Preflight rejection and isolated rollback simulation have passed, but are not equivalent to a live rollback.
- Live-event-specific behavior is only partially observed; deterministic tests and prior match observations are available but do not cover all sports, statuses and provider combinations.
- Third-party code, embedded fonts/sprites, branding and external provider permission questions remain unresolved as described in [THIRD-PARTY-ATTRIBUTION.md](THIRD-PARTY-ATTRIBUTION.md). Endpoint disclosures and user-discretion notices in [DATA-SOURCES.md](DATA-SOURCES.md) do **not** grant access or redistribution rights. These are **open distribution risks**, not resolved licensing checks.

**Technical baseline:** Pi 5 full suite 1,652 passing tests (15 skipped), plus successful Pi 3/Pi 5 operational smoke checks and backup portability. Subsequent changes through this acceptance have been documentation-only; a new full suite is required if executable code changes.

**Release labeling:** Describe any artifact as `v0.8.0 release candidate` with the limitations above. Do not claim a fully verified hardware install, provider authorization, or complete third-party provenance clearance. Final tag/merge remains a separate explicit decision.

## Recommended final smoke procedure

1. Record Pi model, OS release, branch and commit. Keep the known-good SD image and export a portable backup.
2. Verify `sudo ulsctl status` and `sudo ulsctl health`; inspect the browser dashboard and board preview.
3. Confirm live games suppress idle content, and idle content returns only when appropriate. Review sport labels and layouts on the 64×32 display.
4. Edit then cancel an unsaved Content & News change; confirm it remains. Confirm leaving without saving discards it, and returning reloads persisted values.
5. Export a hostname-named portable archive, preview an import, and restore only selected settings on a test device. Verify recovery snapshot and restart services.
6. Check the updater's branch/commit, persistent log and preflight behavior; never intentionally corrupt a production Pi to test rollback.
7. For physical mode, verify driver startup, mapping, brightness, splash, service persistence and output after reboot.
8. Record failures and evidence here before seeking approval.

## Documentation map

- [README](../README.md): quick start, scope and original-project credits.
- [Installation](INSTALLATION.md): supported Trixie system-service install and first-run recovery.
- [Hardware support](HARDWARE-SUPPORT.md) and [RGB driver](RGB-MATRIX-DRIVER.md): physical setup constraints.
- [Dashboard updater](DASHBOARD-UPDATER.md): current status versus historical design notes.
- [Changelog](../CHANGELOG.md): version history.
- [Third-party attribution audit](THIRD-PARTY-ATTRIBUTION.md): provenance and license review still required.
- Older release checklists and preview documents are historical, not current installation instructions.
