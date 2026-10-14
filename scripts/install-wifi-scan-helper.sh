#!/usr/bin/env bash
set -euo pipefail
# Run with sudo from the checked-out repository. Installs ONLY read-only scan permission.
if [[ "${EUID}" -ne 0 ]]; then echo "Run with sudo" >&2; exit 1; fi
USER_NAME="${SUDO_USER:-}"
if [[ -z "$USER_NAME" || "$USER_NAME" == root ]]; then echo "Run via sudo from the scoreboard user" >&2; exit 1; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET=/usr/local/libexec/universal-led-wifi-scan
install -d -o root -g root -m 0755 /usr/local/libexec
install -o root -g root -m 0755 "$ROOT/scripts/universal-led-wifi-scan" "$TARGET"
# Exact executable path, no arguments; never grant blanket nmcli or shell access.
printf '%s ALL=(root) NOPASSWD: %s\n' "$USER_NAME" "$TARGET" > /etc/sudoers.d/universal-led-wifi-scan
chmod 0440 /etc/sudoers.d/universal-led-wifi-scan
visudo -cf /etc/sudoers.d/universal-led-wifi-scan
echo "Read-only Wi-Fi scan helper installed for $USER_NAME"
