#!/usr/bin/env bash
set -Eeuo pipefail
if [[ "$EUID" -ne 0 ]]; then
  echo 'Run with sudo.' >&2
  exit 1
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
install -o root -g root -m 0755 "$ROOT/scripts/uls-restart-services" /usr/local/libexec/uls-restart-services
printf 'uls ALL=(root) NOPASSWD: /usr/local/libexec/uls-restart-services ""\n' > /etc/sudoers.d/uls-dashboard-restart
chmod 0440 /etc/sudoers.d/uls-dashboard-restart
visudo -cf /etc/sudoers.d/uls-dashboard-restart
echo 'Dashboard restart helper installed for the uls service account.'
