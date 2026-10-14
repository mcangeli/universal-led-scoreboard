#!/usr/bin/env bash
set -euo pipefail
# Installs the preflight-only helper and inactive recovery worker.
# No network modifications, systemd recovery units or timers are started.
if [[ "$EUID" -ne 0 ]]; then echo "Run with sudo" >&2; exit 1; fi
USER_NAME="${SUDO_USER:-}"
if [[ -z "$USER_NAME" || "$USER_NAME" == root ]]; then
  echo "Run via sudo from the scoreboard account" >&2; exit 1
fi
if ! [[ "$USER_NAME" =~ ^[a-z_][a-z0-9_-]*[$]?$ ]]; then
  echo "Invalid account name" >&2; exit 1
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIBEXEC=/usr/local/libexec
SUDOERS=/etc/sudoers.d/universal-led-wifi-connect
install -d -o root -g root -m 0755 "$LIBEXEC"
install -o root -g root -m 0755 "$ROOT/scripts/universal-led-wifi-connect" "$LIBEXEC/universal-led-wifi-connect"
install -o root -g root -m 0755 "$ROOT/universal_led/wifi_recovery.py" "$LIBEXEC/universal-led-wifi-recovery"
# Preflight helper accepts no CLI arguments and currently rejects all mutating operations.
TMP="$(mktemp /etc/sudoers.d/.universal-led-wifi-connect.XXXXXX)"
trap 'rm -f "$TMP"' EXIT
printf '%s ALL=(root) NOPASSWD: %s ""\n' "$USER_NAME" "$LIBEXEC/universal-led-wifi-connect" > "$TMP"
chmod 0440 "$TMP"
visudo -cf "$TMP" >/dev/null
install -o root -g root -m 0440 "$TMP" "$SUDOERS"
rm -f "$TMP"
trap - EXIT
echo "Installed preflight-only Wi-Fi helper and inactive recovery worker."
echo "No Wi-Fi settings were changed. Connection switching remains disabled."
