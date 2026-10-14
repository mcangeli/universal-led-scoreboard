# Preview 21.6: guarded Wi-Fi switching

This is an incremental implementation based on the existing
`mcangeli/mlb-scoreboard-configurator` NetworkManager workflow.

## Implemented

- `wifi_connection_plan.py` validates requests and preserves the current
  connection profile for rollback.
- `wifi_recovery.py` implements the **independent rollback worker**. A root-owned
  transient systemd unit will invoke it with an opaque token. It waits up to
  180 seconds, then restores the original NetworkManager connection unless
  the state file has been removed by a verified confirmation operation.
- Tests exercise the timeout, confirmation, and invalid-state paths.

## Not yet implemented

The privileged helper, root-only recovery state writer, systemd unit launcher,
confirmation endpoint, and installer are **not yet present**. Therefore the
recovery worker is not currently armed or running, and the UI's Connect
button remains disabled. Do not call the worker manually or treat this as
production-ready remote Wi-Fi switching.

## Safety requirements for the next stage

1. Only a root-owned helper may create recovery state in
   `/run/universal-led-scoreboard/wifi-recovery`, mode 0700, with files mode 0600.
2. Start an independently managed recovery unit **before** changing networks;
   abort the switch if scheduling recovery fails.
3. Pass credentials via protected standard input or a temporary root-only
   file, never as command-line arguments or in logs.
4. Acknowledge success only after confirming the intended SSID and a viable
   management path. A local association alone is not proof of reachability.
5. On failed verification or timeout, restore the original profile. Test with
   local console access before enabling remote use.
6. Reuse the MLB configurator's hotspot state machine, but keep its privileged
   operations inside the restricted helper.

Test with `python3 -m unittest discover -s tests -v`.
