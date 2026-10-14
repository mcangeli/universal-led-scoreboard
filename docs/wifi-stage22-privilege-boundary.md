# Stage 22: Wi-Fi connection privilege boundary

## Verified baseline
Stage 21 exercised recovery scheduling, root-owned transient systemd worker,
confirmation, and live rollback of an intentionally disconnected wlan0, while
Ethernet remained available. The configurator's Connect button remains disabled.

## Required boundary before connection switching
The HTTP configurator must remain unprivileged. Do not run the web server as
root, grant broad passwordless sudo, or accept arbitrary shell commands.

A dedicated privileged operation boundary must:
- expose a fixed allowlist of actions (prepare, confirm, inspect);
- validate interface names and NetworkManager connection identifiers;
- authenticate and authorize the local caller independently of web login;
- reject arbitrary command paths, filenames, and systemd unit names;
- never expose Wi-Fi passwords in arguments, logs, or status responses;
- arm and verify recovery before attempting a connection change;
- report confirmation separately from successful systemd stop;
- enforce a single pending switch per interface;
- preserve the prior connection and support a bounded recovery deadline.

## Proposed implementation sequence
1. Add a pure, testable request schema and state machine. No system calls.
2. Define a narrowly scoped privileged helper transport and deployment model.
3. Exercise mocked authorization, concurrency, and failure-path tests.
4. Integrate read-only operation status in the authenticated configurator.
5. Test the helper on the Pi using Ethernet SSH, first without switching Wi-Fi.
6. Supervise a real change between two known-good Wi-Fi profiles.
7. Enable Connect only after rollback and confirmation succeed end-to-end.

## Known limitation
A successful rollback to the same saved profile does not establish that a
different network's credentials, DHCP, DNS, or routing can be handled safely.
The UI must continue to present switching as unavailable.
