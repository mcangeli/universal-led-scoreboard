#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$(command -v python3)"
UNIT_DIR="${HOME}/.config/systemd/user"
mkdir -p "$UNIT_DIR"
cat > "$UNIT_DIR/universal-led-scoreboard.service" <<EOF
[Unit]
Description=Universal LED Scoreboard Web Configurator and Emulator
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$ROOT
ExecStart=$PYTHON -m universal_led.configurator --host 0.0.0.0 --port 8080
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload
systemctl --user enable --now universal-led-scoreboard.service
echo "Service installed. Open http://YOUR_PI_IP:8080/ and http://YOUR_PI_IP:8080/board"
echo "Status: systemctl --user status universal-led-scoreboard.service"
echo "Logs: journalctl --user -u universal-led-scoreboard.service -f"
