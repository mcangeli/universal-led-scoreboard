#!/usr/bin/env bash
set -euo pipefail
if [[ "$EUID" -ne 0 || -z "${SUDO_USER:-}" || "$SUDO_USER" == root ]]; then
  echo 'Run with sudo from scoreboard account' >&2; exit 1
fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST=/usr/local/libexec/universal-led-wifi-python
install -d -o root -g root -m 0755 "$DEST/universal_led"
# Install only the privileged bridge and its recovery dependencies, root-owned.
for name in wifi_privileged_bridge wifi_recovery_scheduler wifi_recovery_confirmation wifi_recovery_cancellation wifi_recovery wifi_recovery_safe_file; do
  install -o root -g root -m 0644 "$ROOT/universal_led/$name.py" "$DEST/universal_led/$name.py"
done
printf '' > "$DEST/universal_led/__init__.py"
chown root:root "$DEST/universal_led/__init__.py"
chmod 0644 "$DEST/universal_led/__init__.py"
install -d -o root -g root -m 0755 /usr/local/libexec
# Recovery scheduler invokes this exact root-owned standalone worker.
install -o root -g root -m 0755 "$ROOT/universal_led/wifi_recovery.py" /usr/local/libexec/universal-led-wifi-recovery
cat > /usr/local/libexec/universal-led-wifi-control <<'EOF'
#!/usr/bin/python3 -I
import sys
sys.path.insert(0, '/usr/local/libexec/universal-led-wifi-python')
from universal_led.wifi_privileged_bridge import main
main()
EOF
chown root:root /usr/local/libexec/universal-led-wifi-control
chmod 0755 /usr/local/libexec/universal-led-wifi-control
printf '%s ALL=(root) NOPASSWD: /usr/local/libexec/universal-led-wifi-control ""\n' "$SUDO_USER" > /etc/sudoers.d/universal-led-wifi-control
chmod 0440 /etc/sudoers.d/universal-led-wifi-control
visudo -cf /etc/sudoers.d/universal-led-wifi-control
# Syntax-check installed files before reporting success.
python3 -m py_compile "$DEST"/universal_led/*.py
echo 'Scoped Wi-Fi control and recovery workers installed; no network settings changed.'
