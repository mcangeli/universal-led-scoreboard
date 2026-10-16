#!/usr/bin/env bash
# Provision a disabled-by-default NetworkManager recovery AP without exposing its PSK in argv.
set -Eeuo pipefail
(( EUID == 0 )) || { echo "Run as root" >&2; exit 1; }
PROFILE=Universal-LED-Setup
SECRET_DIR=/etc/uls/secrets
SECRET_FILE="$SECRET_DIR/hotspot-password"
install -d -o root -g root -m 0700 "$SECRET_DIR"
if [[ ! -f "$SECRET_FILE" ]]; then
  umask 077
  python3 - "$SECRET_FILE" <<'PY'
import secrets,sys,os
from pathlib import Path
path=Path(sys.argv[1])
password=secrets.token_urlsafe(24)
fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as f: f.write(password+'\n')
PY
fi
chmod 0600 "$SECRET_FILE"
if ! nmcli -g connection.id connection show "$PROFILE" >/dev/null 2>&1; then
  nmcli connection add type wifi ifname '*' con-name "$PROFILE" ssid "$PROFILE" \
    802-11-wireless.mode ap ipv4.method shared ipv6.method disabled \
    connection.autoconnect no wifi-sec.key-mgmt wpa-psk >/dev/null
fi
# Use nmcli editor stdin so the password never appears in command arguments.
python3 - "$SECRET_FILE" <<'PY' | nmcli connection edit "$PROFILE" >/dev/null
from pathlib import Path
import sys
password=Path(sys.argv[1]).read_text().strip()
print('set wifi-sec.psk "'+password+'"')
print('save persistent')
print('quit')
PY
nmcli connection modify "$PROFILE" connection.autoconnect no >/dev/null
echo "Recovery hotspot profile provisioned (disabled by default)."
echo "Hotspot password stored in $SECRET_FILE; retrieve locally with sudo."
