#!/usr/bin/env bash
# Stage Universal LED Scoreboard in conventional system directories.
# Existing user service remains untouched until the administrator switches over.
set -Eeuo pipefail
SOURCE_DIR="${SOURCE_DIR:-$HOME/universal-led-scoreboard}"
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) echo "Usage: bash scripts/migrate-to-opt.sh [--dry-run]"; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done
if (( EUID == 0 )); then echo "Run as your regular user (sudo is invoked when needed)." >&2; exit 1; fi
[[ -f "$SOURCE_DIR/universal_led/configurator.py" ]] || { echo "Source checkout missing: $SOURCE_DIR" >&2; exit 1; }
echo "Source: $SOURCE_DIR"
echo "Destination: /opt/uls/app"
echo "Configuration: /etc/uls"
echo "Persistent data: /var/lib/uls"
echo "Runtime frames: /run/uls"
echo "Existing user service will NOT be stopped or changed."
if (( DRY_RUN )); then exit 0; fi
sudo install -d -m 0755 /opt/uls /opt/uls/app
sudo install -d -m 0700 /etc/uls /etc/uls/secrets
sudo install -d -m 0755 /var/lib/uls /var/lib/uls/data
sudo install -d -m 0755 /opt/uls/drivers
sudo cp -a "$SOURCE_DIR/." /opt/uls/app/
# Preserve settings from existing user install without overwriting migrated values.
LEGACY_CONFIG="$HOME/.config/universal-led-scoreboard"
if [[ -d "$LEGACY_CONFIG" ]]; then
  sudo cp -an "$LEGACY_CONFIG/." /etc/uls/\n  sudo rm -f /etc/uls/live-frame.ppm
fi
# Restrict copied secrets, which may include administrator hashes and API keys.
sudo rm -f /etc/uls/live-frame.ppm\nsudo chmod 0700 /etc/uls /etc/uls/secrets
sudo find /etc/uls -type f -exec chmod 0600 {} +
# Copy the verified driver environment without rebuilding or changing the original.
LEGACY_VENV="$HOME/.local/share/universal-led-scoreboard/matrix-venv"
if [[ -d "$LEGACY_VENV" && ! -e /opt/uls/venv ]]; then
  echo "Existing matrix virtual environment retained at $LEGACY_VENV."
  echo "A fresh /opt/uls/venv will be created during service cutover."
fi
sudo tee /etc/tmpfiles.d/uls.conf >/dev/null <<'EOF'
d /run/uls 0755 root root -
EOF
sudo systemd-tmpfiles --create /etc/tmpfiles.d/uls.conf
echo "Staging complete. Existing service still runs from $SOURCE_DIR."
echo "Review /opt/uls/app and /etc/uls before switching services."
