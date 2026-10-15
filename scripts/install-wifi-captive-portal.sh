#!/usr/bin/env bash
set -euo pipefail
if [[ "$EUID" -ne 0 ]]; then echo 'Run with sudo' >&2; exit 1; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE=Universal-LED-Setup
GATEWAY=10.42.0.1
# Refuse to modify unexpected network profiles or subnet configurations.
MODE="$(nmcli -g 802-11-wireless.mode connection show "$PROFILE" 2>/dev/null || true)"
METHOD="$(nmcli -g ipv4.method connection show "$PROFILE" 2>/dev/null || true)"
ADDRESSES="$(nmcli -g ipv4.addresses connection show "$PROFILE" 2>/dev/null || true)"
if [[ "$MODE" != ap || "$METHOD" != shared ]]; then
  echo 'Expected dedicated NetworkManager shared hotspot profile' >&2; exit 1
fi
if [[ -n "$ADDRESSES" && "$ADDRESSES" != 10.42.0.1/24 ]]; then
  echo "Custom hotspot subnet detected ($ADDRESSES); captive portal not installed" >&2; exit 1
fi
# Configure a deterministic gateway only for the dedicated hotspot.
# Changing the profile does not interrupt the currently active connection.
if [[ -z "$ADDRESSES" ]]; then
  nmcli connection modify "$PROFILE" ipv4.addresses "$GATEWAY/24"
fi
install -d -o root -g root -m 0755 /usr/local/libexec/universal-led-wifi-python/universal_led
install -o root -g root -m 0644 "$ROOT/universal_led/wifi_captive_portal.py" /usr/local/libexec/universal-led-wifi-python/universal_led/wifi_captive_portal.py
cat > /usr/local/libexec/universal-led-wifi-portal <<'EOF'
#!/usr/bin/python3 -I
import sys
sys.path.insert(0, '/usr/local/libexec/universal-led-wifi-python')
from universal_led.wifi_captive_portal import main
main()
EOF
chmod 0755 /usr/local/libexec/universal-led-wifi-portal
chown root:root /usr/local/libexec/universal-led-wifi-portal
# NetworkManager's dedicated shared-mode dnsmasq reads these options.
# This affects DNS for NetworkManager shared-mode connections; do not
# install on systems using other shared-mode interfaces.
install -d -o root -g root -m 0755 /etc/NetworkManager/dnsmasq-shared.d
cat > /etc/NetworkManager/dnsmasq-shared.d/universal-led-captive.conf <<'EOF'
# Captive detection on Universal-LED-Setup shared-mode gateway.
address=/#/10.42.0.1
EOF
cat > /etc/systemd/system/universal-led-wifi-portal.service <<'EOF'
[Unit]
Description=Universal LED captive portal landing service
After=NetworkManager.service
[Service]
Type=simple
ExecStart=/usr/local/libexec/universal-led-wifi-portal
Restart=on-failure
RestartSec=10
User=root
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now universal-led-wifi-portal.service
echo 'Captive portal installed. Reactivate the hotspot to apply gateway and DNS changes.'
echo 'Manual fallback: http://10.42.0.1:8080/login'
