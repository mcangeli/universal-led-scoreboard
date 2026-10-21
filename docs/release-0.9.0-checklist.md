# ULS 0.9.0 release candidate checklist

Scope: dynamic team registry, native external plugin lifecycle, official plugin catalog, and plugin rotation. Google Calendar OAuth is a separate **external plugin** enhancement and is not a Core 0.9.0 blocker.

## Code and compatibility gates

- [x] Pi 5 updater preflight and installation accepted by operator on 2026-10-21, after offline catalog regression fix (commit `f3f2593` and subsequent checklist-only commit). Exact final test count not supplied.
- [x] Pi 3 updater preflight and installation also accepted by operator on 2026-10-21; both devices updated successfully. Latest verified Pi 3 run: commit `5ec14c9`, **1,797 tests, 15 skipped, zero failures**, successful fast-forward installation on 2026-10-21; updater confirms `/etc/uls` and `/var/lib/uls` untouched.
- [ ] Confirm no pending configuration/schema migration errors on existing installations.
- [ ] Verify dynamic team selections and favorites persist through dashboard save, service restart, and backup/restore.
- [ ] Confirm live games preempt supplemental plugin screens, and non-live rotation interleaves regular ULS content between enabled plugins.
- [ ] Confirm plugins honor per-plugin display duration and enable/disable state after restart.
- [ ] Verify plugin install, update, uninstall, and failed-install rollback with a test plugin.
- [ ] Confirm official catalog loads remotely, uses cached data offline, and falls back to the bundled catalog when necessary.
- [ ] Confirm catalog entries and versions match external plugin manifests (run external repository's `python -m unittest discover -s tests -v`).
- [ ] Check that secret plugin settings and tokens do not appear in logs or exported support diagnostics.
- [ ] Verify matrix display on Pi 3, and browser board preview on Pi 5.
- [ ] Verify fresh install and existing-install upgrade paths on supported OS targets.

## Documentation and release gates

- [ ] Update installation, upgrade, recovery, plugin developer, and troubleshooting instructions.
- [ ] Document supported Pi hardware, OS versions, and known limitations.
- [ ] Prepare v0.9.0 changelog and release notes.
- [ ] Create an annotated release candidate tag after both devices pass.
- [ ] Recheck the release candidate, then merge/tag stable v0.9.0 only after acceptance.

## Explicitly deferred

- Automatic **update-available notifications**: v1.0.0. Updates remain administrator-approved.
- Daily Calendar direct Google OAuth, recurrence and faster Google API sync: external `uls-plugins` release.
- Any new plugin feature unrelated to Core release stability.

Record hardware checks and test results here before release. A passing source-inspection test alone is not hardware acceptance.
