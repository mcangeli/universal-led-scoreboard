#!/usr/bin/env bash
# Change the matrix worker interpreter, reverting the unit on failure.
set -Eeuo pipefail
[[ $EUID -ne 0 ]] || { echo "Run as the regular installer user." >&2; exit 1; }
UNIT=/etc/systemd/system/uls-matrix.service
NEW=/opt/uls/venv/bin/python
[[ -f "$UNIT" && -x "$NEW" ]] || { echo "Missing unit or prepared venv." >&2; exit 1; }
"$NEW" -c 'from rgbmatrix import RGBMatrix, RGBMatrixOptions'
sudo systemctl is-active --quiet uls-matrix.service || { echo "Matrix worker must be running before switching." >&2; exit 1; }
BACKUP="$UNIT.backup-$(date +%Y%m%d%H%M%S)"
sudo cp -a "$UNIT" "$BACKUP"
rollback() {
  echo "Matrix switch failed. Restoring old unit." >&2
  sudo cp -a "$BACKUP" "$UNIT"
  sudo systemctl daemon-reload
  sudo systemctl restart uls-matrix.service || true
}
trap rollback ERR
sudo sed -i -E 's@^ExecStart=[^ ]+/bin/python(3)? -m universal_led.matrix_worker@ExecStart=/opt/uls/venv/bin/python -m universal_led.matrix_worker@' "$UNIT"
grep -q '^ExecStart=/opt/uls/venv/bin/python -m universal_led.matrix_worker' "$UNIT"
sudo systemctl daemon-reload
sudo systemctl restart uls-matrix.service
sleep 3
sudo systemctl is-active --quiet uls-matrix.service
sudo systemctl is-failed --quiet uls-matrix.service && exit 1
trap - ERR
echo "Matrix service now uses /opt/uls/venv/bin/python."
echo "Backup: $BACKUP"
echo "Verify the physical panel and check: sudo journalctl -u uls-matrix -n 30 --no-pager"
