#!/usr/bin/env bash
# Prepare system services without disrupting the existing user service.
set -Eeuo pipefail
[[ $EUID -ne 0 ]] || { echo "Run as regular user, not root." >&2; exit 1; }
[[ -f /opt/uls/app/universal_led/configurator.py ]] || { echo "Run migration first." >&2; exit 1; }
[[ -f /etc/uls/admin.json ]] || { echo "Missing migrated administrator credentials." >&2; exit 1; }
id uls >/dev/null 2>&1 || sudo useradd --system --home-dir /var/lib/uls --shell /usr/sbin/nologin uls
sudo chown -R uls:uls /etc/uls /var/lib/uls
sudo chmod 0700 /etc/uls /etc/uls/secrets
sudo find /etc/uls -type f -exec chmod 0600 {} +
sudo tee /etc/tmpfiles.d/uls.conf >/dev/null <<'EOF'
d /run/uls 0755 uls uls -
EOF
sudo systemd-tmpfiles --create /etc/tmpfiles.d/uls.conf
sudo chown uls:uls /run/uls
# Run web on 8081 during validation so port 8080 stays with the legacy service.
sudo tee /etc/systemd/system/uls-web.service >/dev/null <<'EOF'
[Unit]
Description=Universal LED Scoreboard Web Configurator
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=uls
Group=uls
WorkingDirectory=/opt/uls/app
Environment=HOME=/var/lib/uls
Environment=ULS_FRAME_FILE=/run/uls/live-frame.ppm
ExecStart=/usr/bin/python3 -m universal_led.configurator --host 0.0.0.0 --port 8081 --config-dir /etc/uls
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
MATRIX_PY="$HOME/.local/share/universal-led-scoreboard/matrix-venv/bin/python"
if [[ -x "$MATRIX_PY" ]]; then
  sudo tee /etc/systemd/system/uls-matrix.service >/dev/null <<EOF
[Unit]
Description=Universal LED Scoreboard Physical Matrix
After=uls-web.service
Wants=uls-web.service

[Service]
Type=simple
WorkingDirectory=/opt/uls/app
ExecStart=$MATRIX_PY -m universal_led.matrix_worker --frame-file /run/uls/live-frame.ppm --mapping adafruit-hat --brightness 40 --gpio-slowdown 4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
else
  echo "Matrix venv missing; physical service not installed." >&2
fi
sudo systemctl daemon-reload
echo "Service units staged. Neither service was started or enabled."
echo "Next: sudo systemctl start uls-web && sudo systemctl status uls-web"
echo "Legacy port 8080 remains untouched; staged service uses port 8081."
