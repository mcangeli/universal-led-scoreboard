#!/usr/bin/env bash
set -Eeuo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run with sudo' >&2; exit 1; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
install -d -o root -g root -m 0755 /usr/local/libexec
for name in uls-update-status uls-update-launch uls-update-worker uls-update-select; do
  install -o root -g root -m 0755 "$ROOT/scripts/$name" "/usr/local/libexec/$name"
done
tmp=$(mktemp /etc/sudoers.d/.uls-dashboard-update.XXXXXX)
trap 'rm -f "$tmp"' EXIT
printf 'uls ALL=(root) NOPASSWD: /usr/local/libexec/uls-update-status "", /usr/local/libexec/uls-update-launch "", /usr/local/libexec/uls-update-select ""\n' > "$tmp"
chmod 0440 "$tmp"
visudo -cf "$tmp" >/dev/null
install -o root -g root -m 0440 "$tmp" /etc/sudoers.d/uls-dashboard-update
install -d -o root -g uls -m 0750 /var/lib/uls/update
echo 'Dashboard updater helper installed.'
