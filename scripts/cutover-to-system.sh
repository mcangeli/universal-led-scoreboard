#!/usr/bin/env bash
# Cut over only after both staged services have been tested.
set -Eeuo pipefail
[[ $EUID -ne 0 ]] || { echo "Run as the regular installer user." >&2; exit 1; }
LEGACY=universal-led-scoreboard.service
WEB=uls-web.service
MATRIX=uls-matrix.service
UNIT=/etc/systemd/system/uls-web.service
[[ -f "$UNIT" ]] || { echo "Missing $UNIT" >&2; exit 1; }
sudo systemctl is-active --quiet "$WEB" || { echo "Start and verify uls-web on 8081 first." >&2; exit 1; }
sudo systemctl is-active --quiet "$MATRIX" || { echo "Start and verify uls-matrix first." >&2; exit 1; }
curl --fail --silent --output /dev/null http://127.0.0.1:8081/ || { echo "New configurator did not respond on 8081." >&2; exit 1; }
[[ -s /run/uls/live-frame.ppm ]] || { echo "No published framebuffer." >&2; exit 1; }
BACKUP="$UNIT.backup-$(date +%Y%m%d%H%M%S)"
sudo cp -a "$UNIT" "$BACKUP"
LEGACY_ACTIVE=0
LEGACY_ENABLED=0
systemctl --user is-active --quiet "$LEGACY" && LEGACY_ACTIVE=1 || true
systemctl --user is-enabled --quiet "$LEGACY" && LEGACY_ENABLED=1 || true
rollback() {
  echo "Cutover failed; restoring port 8081 and original user service." >&2
  sudo cp -a "$BACKUP" "$UNIT"
  sudo systemctl daemon-reload
  sudo systemctl restart "$WEB" || true
  if (( LEGACY_ENABLED )); then systemctl --user enable "$LEGACY" || true; fi
  if (( LEGACY_ACTIVE )); then systemctl --user restart "$LEGACY" || true; fi
}
trap rollback ERR
systemctl --user stop "$LEGACY" || true
systemctl --user disable "$LEGACY" || true
sudo sed -i 's/--port 8081 /--port 8080 /' "$UNIT"
grep -q -- '--port 8080 ' "$UNIT"
sudo systemctl daemon-reload
sudo systemctl restart "$WEB"
for i in {1..20}; do
  if curl --fail --silent --output /dev/null http://127.0.0.1:8080/; then break; fi
  sleep 1
done
curl --fail --silent --output /dev/null http://127.0.0.1:8080/
sudo systemctl enable "$WEB" "$MATRIX"
sudo systemctl is-active --quiet "$WEB"
sudo systemctl is-active --quiet "$MATRIX"
trap - ERR
echo "Cutover complete. New web service is on port 8080."
echo "Legacy service is disabled but its files are preserved."
echo "Unit backup: $BACKUP"
