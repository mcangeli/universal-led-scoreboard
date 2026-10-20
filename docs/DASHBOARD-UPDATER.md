# Dashboard software updater: architecture and historical design notes

**Current status (v0.8.0 release candidate):** Dashboard-driven updates have been exercised on Raspberry Pi installations with preflight test rejection and successful fast-forward installation. Candidate failures leave the installed commit and persistent configuration unchanged. The updater retains progress logs across dashboard restarts; branch selection and compatibility checks are implemented. The documented original design and acceptance checklist below are historical specifications, **not proof that every failure/rollback scenario has been tested**. Consult [CHANGELOG](../CHANGELOG.md) for current acceptance evidence. Portable backup export/import is managed separately from the updater, under Dashboard → Maintenance tools; its recovery snapshot does not replace a full software rollback.

## Original design: user experience

A **Software Updates** section in System and a compact Dashboard status display:
- Installed commit and branch.
- Check for updates, showing remote commit and ahead/behind state.
- Explicit **Install Update** confirmation with notice that web and matrix services restart.
- Persisted stage/log output and outcome so browser refreshes and web restarts do not lose progress.
- An update must not be reported successful until the updater confirms the final health check.

## Privilege boundary

The web process runs as `uls` and **must not** execute arbitrary Git or shell commands as root. Implement two root-owned, argument-free executables with narrow sudoers permissions:
- `/usr/local/libexec/uls-check-update`: query only the configured repository and branch. Return bounded, machine-readable status. Do not accept a user-provided repository, branch, or path.
- `/usr/local/libexec/uls-start-update`: atomically lock and launch the existing `/opt/uls/app/scripts/uls-update` in a detached systemd unit. Reject concurrent updates. Never accept command arguments.

The web API requires a valid administrator session for reads and the existing anti-CSRF token for POST. Reject requests that attempt to specify a Git URL, branch, command, or filesystem path.

## Progress and recovery

The detached updater writes a bounded root-controlled log/status under `/var/lib/uls/update`, readable by the web service but not writable by it. Record queued, fetching, testing, installing, restarting, verifying, completed, and failed/rollback states. A web-service restart must not kill the updater. Status endpoints should distinguish a stale or crashed job from a running one.

Avoid exposing credentials or secrets in logs. Do not use an unbounded shell output capture in a request handler. Do not call `sudo ulsctl update` synchronously from the web request.

## Installation and compatibility

- Install helpers and scoped sudoers rules from `scripts/install-system.sh` and provide an idempotent migration helper for existing systems.
- Existing `sudo ulsctl update` remains supported and shares the same lock with dashboard-triggered updates.
- The current updater assumes a physical matrix service exists. Before enabling dashboard update on emulator-only installs, teach the updater and `ulsctl health` to handle that mode.
- Continue rejecting dirty checkouts, non-fast-forward changes, and failed candidate tests.

## Acceptance tests

1. Anonymous GET and POST denied; authenticated POST without CSRF denied.
2. No arbitrary URL, ref, or command input accepted.
3. No-update and available-update responses are accurate.
4. Concurrent update attempts rejected.
5. Tests run before Git fast-forward; failures preserve current installation.
6. Detached updater survives `uls-web.service` restart and updates progress.
7. Installed CLI synchronizes; health is verified before success.
8. Failed update attempts rollback and leaves diagnostics accessible.
9. Works on fresh Trixie physical install and existing upgraded Pi 5.
10. Does not claim success for emulator mode until its service assumptions are fixed.
