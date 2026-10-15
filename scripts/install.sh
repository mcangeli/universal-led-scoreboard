#!/usr/bin/env bash
set -Eeuo pipefail
SERVICE="universal-led-scoreboard.service"
PORT=8080
SKIP_APT=0
NO_START=0
INSTALL_DIR="$HOME/universal-led-scoreboard"
usage() {
  echo "Usage: bash scripts/install.sh [--skip-apt] [--no-start] [--port 8080] [--install-dir PATH]"
  echo "Installs web configurator and emulator, NOT physical matrix drivers."
}
while (($#)); do
  case "$1" in
    --skip-apt) SKIP_APT=1; shift ;;
    --no-start) NO_START=1; shift ;;
    --port) PORT="$2"; shift 2 ;;
    --install-dir) INSTALL_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
if ((EUID == 0)); then echo "Run as the regular Pi user, not sudo." >&2; exit 1; fi
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || ((PORT < 1 || PORT > 65535)); then echo "Invalid port" >&2; exit 2; fi
if [[ ! -f "$INSTALL_DIR/universal_led/configurator.py" ]]; then
  echo "Missing checkout at $INSTALL_DIR. Clone the repository first." >&2; exit 1
fi
if ((SKIP_APT == 0)); then
  sudo apt-get update
  sudo apt-get install -y python3 python3-venv python3-pip git
fi
INSTALL_DIR="$(cd "$INSTALL_DIR" && pwd -P)"
CONFIG_DIR="$HOME/.config/universal-led-scoreboard"
UNIT_DIR="$HOME/.config/systemd/user"
mkdir -p "$CONFIG_DIR" "$UNIT_DIR"
chmod 700 "$CONFIG_DIR"
if [[ ! -f "$CONFIG_DIR/admin.json" ]]; then
  (cd "$INSTALL_DIR" && python3 -m universal_led.configurator --config-dir "$CONFIG_DIR" --set-admin-password)
else
  echo "Existing administrator password preserved."
fi
UNIT="$UNIT_DIR/$SERVICE"
if [[ -f "$UNIT" ]]; then cp -p "$UNIT" "$UNIT.backup-$(date +%Y%m%d%H%M%S)"; fi
# systemd supports quoted paths; reject unusual paths to avoid ambiguous unit parsing.
if [[ "$INSTALL_DIR" == *$'\n'* || "$INSTALL_DIR" == *'"'* || "$INSTALL_DIR" == *'%'* ]]; then
  echo "Installation path contains unsupported characters" >&2; exit 1
fi
cat > "$UNIT" <<EOF
[Unit]
Description=Universal LED Scoreboard Web Configurator
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 -m universal_led.configurator --host 0.0.0.0 --port $PORT --config-dir $CONFIG_DIR
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable "$SERVICE"
if ((NO_START == 0)); then systemctl --user restart "$SERVICE"; fi
if command -v loginctl >/dev/null && [[ "$(loginctl show-user "$USER" -p Linger --value 2>/dev/null || true)" != yes ]]; then
  sudo loginctl enable-linger "$USER"
fi
echo "Installed. Open http://$(hostname -I | awk '{print $1}'):$PORT"
echo "Check: systemctl --user status $SERVICE"
echo "Logs: journalctl --user -u $SERVICE -n 100 --no-pager"
echo "RGB matrix hardware output has NOT been enabled."
