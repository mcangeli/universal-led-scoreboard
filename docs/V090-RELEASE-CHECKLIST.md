# v0.9.0 release acceptance checklist

**Status:** feature branch candidate; not yet merged or tagged. Scope: dynamic team registry, native Plugin Manager, TOML manifests and JSON backward compatibility. Native Magic Number and Green Monster plugin releases are **out of scope**.

## Confirmed

- [x] Pi 5 dashboard updater installed commit `bea17cc` successfully on 2026-10-20.
- [x] Candidate preflight: **1,782 tests run, 15 skipped, no failures**.
- [x] Existing `/etc/uls` configuration and `/var/lib/uls` persistent state preserved.
- [x] Native TOML manifest tests: four passed.
- [x] Swimming Fish upgraded from JSON manifest to TOML and continued rendering.
- [x] Abandoned Bullpen adapter scaffolding removed from Core.
- [x] Native plugin developer guide updated: [PLUGIN-DEVELOPMENT.md](PLUGIN-DEVELOPMENT.md).

## Still to verify before release tagging

- [x] Full regression suite on documentation commit `2940b65`: **1,782 tests run, 15 skipped, no failures**; Pi 5 dashboard updater completed successfully on 2026-10-20.
- [x] Pi 5 Swimming Fish plugin lifecycle: install, enable, render, disable, uninstall and reinstall verified by user (2026-10-21). Settings and animation verified after reinstallation.
- [x] Swimming Fish TOML update rendered correctly; user subsequently confirmed settings and animation after reinstallation and service restart (2026-10-21).
- [x] Pi 5 dashboard favorite-team changes retain the saved selections (user-verified, 2026-10-21).
- [ ] Dynamic team registry remaining acceptance: restart persistence, sports coverage, and existing saved-config compatibility.
- [ ] Pi 3 production candidate preflight and physical 64×32 output observation.
- [ ] Confirm source attribution, dependencies and remaining accepted release-candidate exceptions.
- [ ] Review release notes, merge branch to `main`, create `v0.9.0-rc.1`, and verify production update.

Do not treat an automated test pass as proof of physical hardware behavior. The invalid-brightness CLI error in the candidate test log is an expected negative test. Third-party Python plugins are trusted code, **not sandboxed**.
