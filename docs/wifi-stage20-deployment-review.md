# Preview 21.6 Stage 20: Wi-Fi recovery deployment review

Stage 20 provides **read-only deployment inspection**. It does not install the
privileged worker, arm a recovery unit, change NetworkManager settings, or
enable the Wi-Fi Connect button.

## Inspect on the Pi

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -c 'from universal_led.wifi_deployment_preflight import deployment_preflight; import json; print(json.dumps(deployment_preflight(), indent=2))'
```

The authenticated configurator System > Wi-Fi page displays the same preflight
result. An incomplete result is expected when the worker has not been installed.

## What the preflight checks

- Recovery source is a regular, single-linked file.
- python3, systemd-run, systemctl, and nmcli are available.
- Installed worker is a root-owned, single-linked regular executable with mode
  0755.
- Installed worker bytes match the repository recovery source.

## Not yet authorized

Do not manually install or execute the privileged worker on a remotely managed
Pi based on this document. Do not use the root scheduler to switch networks.
Before enabling live switching, the integration phase must review privilege
boundaries, transient unit behavior, recovery cancellation, deployment/rollback,
and a supervised end-to-end test with alternate access to the Pi.

A successful preflight is **not** proof that rollback will restore connectivity.
