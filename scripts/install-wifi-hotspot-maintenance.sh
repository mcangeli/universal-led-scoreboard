#!/usr/bin/env bash
set -euo pipefail
if [[ "$EUID" -ne 0 ]]; then echo 'Run with sudo' >&2; exit 1; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST=/usr/local/libexec/universal-led-wifi-python
install -d -o root -g root -m 0755 "$DEST/universal_led"
install -o root -g root -m 0644 "$ROOT/universal_led/wifi_hotspot_maintenance.py" "$DEST/universal_led/wifi_hotspot_maintenance.py"
install -o root -g root -m 0644 "$ROOT/universal_led/wifi_diagnostics.py" "$DEST/universal_led/wifi_diagnostics.py"
if [[ ! -f "$DEST/universal_led/__init__.py" ]]; then install -o root -g root -m 0644 /dev/null "$DEST/universal_led/__init__.py"; fi
cat > /usr/local/libexec/universal-led-wifi-maintain <<'EOF'
#!/usr/bin/python3 -I
import sys
sys.path.insert(0, '/usr/local/libexec/universal-led-wifi-python')
from universal_led.wifi_hotspot_maintenance import main
main()
EOF
chown root:root /usr/local/libexec/universal-led-wifi-maintain
chmod 0755 /usr/local/libexec/universal-led-wifi-maintain
cat > /etc/systemd/system/universal-led-wifi-maintain.service <<'EOF'
[Unit]
Description=Universal LED Wi-Fi fallback check
After=NetworkManager.service
Requires=NetworkManager.service
[Service]
Type=oneshot
ExecStart=/usr/local/libexec/universal-led-wifi-maintain
EOF
cat > /etc/systemd/system/universal-led-wifi-maintain.timer <<'EOF'
[Unit]
Description=Periodic Universal LED Wi-Fi recovery
[Timer]
OnBootSec=90s
OnUnitInactiveSec=2min
Unit=universal-led-wifi-maintain.service
[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now universal-led-wifi-maintain.timer
echo 'Wi-Fi maintenance timer enabled. It will not touch Ethernet.'
