#!/usr/bin/env bash
set -Eeuo pipefail
SERVICE="universal-led-scoreboard.service"
PORT=8080
SKIP_APT=0
NO_START=0
OUTPUT_MODE=""
INSTALL_DIR="$HOME/universal-led-scoreboard"
usage() {
  echo "Usage: bash scripts/install.sh [--skip-apt] [--no-start] [--port 8080] [--install-dir PATH] [--output physical|emulator|both|keep]"
  echo "Optionally installs physical RGB matrix driver bindings."
}
while (($#)); do
  case "$1" in
    --output) OUTPUT_MODE="${2:-}"; shift 2 ;;
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
# Output choice is preserved on upgrades unless explicitly changed.
OUTPUT_FILE="$HOME/.config/universal-led-scoreboard/output-mode"
if [[ -z "$OUTPUT_MODE" ]]; then
  if [[ -t 0 ]]; then
    echo "Display output: 1) Physical LED Matrix  2) Browser Emulator  3) Both  4) Keep existing"
    read -r -p "Selection [4]: " selection
    case "${selection:-4}" in
      1) OUTPUT_MODE=physical ;; 2) OUTPUT_MODE=emulator ;;
      3) OUTPUT_MODE=both ;; 4) OUTPUT_MODE=keep ;;
      *) echo "Invalid selection" >&2; exit 2 ;;
    esac
  else
    OUTPUT_MODE=keep
  fi
fi
case "$OUTPUT_MODE" in
  physical|emulator|both|keep) ;;
  *) echo "Invalid --output (physical|emulator|both|keep)" >&2; exit 2 ;;
esac
if [[ "$OUTPUT_MODE" == keep ]]; then
  OUTPUT_MODE="$(cat "$OUTPUT_FILE" 2>/dev/null || echo emulator)"
fi
if [[ "$OUTPUT_MODE" == physical || "$OUTPUT_MODE" == both ]]; then
  MATRIX_PY="$HOME/.local/share/universal-led-scoreboard/matrix-venv/bin/python"
  if [[ -x "$MATRIX_PY" ]] && "$MATRIX_PY" -c "from rgbmatrix import RGBMatrix, RGBMatrixOptions" >/dev/null 2>&1; then
    echo "Existing RGBMatrix Python bindings verified; skipping driver rebuild."
  else
  echo "Installing optional HUB75 matrix Python bindings..."
  if ((SKIP_APT == 0)); then
    sudo apt-get install -y build-essential python3-dev python3-venv python3-pip python3-setuptools cython3 cmake ninja-build
  fi
  DRIVER_DIR="$HOME/.local/src/rpi-rgb-led-matrix"
  mkdir -p "$(dirname "$DRIVER_DIR")"
  if [[ -d "$DRIVER_DIR/.git" ]]; then
    git -C "$DRIVER_DIR" pull --ff-only
  elif [[ ! -e "$DRIVER_DIR" ]]; then
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git "$DRIVER_DIR"
  else
    echo "Driver directory exists but is not a Git checkout: $DRIVER_DIR" >&2; exit 1
  fi
  make -C "$DRIVER_DIR/lib"
  python3 -m venv --system-site-packages "$HOME/.local/share/universal-led-scoreboard/matrix-venv"
  MATRIX_PY="$HOME/.local/share/universal-led-scoreboard/matrix-venv/bin/python"
  # Upstream switched to a root-level pyproject.toml (scikit-build-core) in 2026.
  # Older checkouts used root-level Makefile targets instead.
  if [[ -f "$DRIVER_DIR/pyproject.toml" ]]; then
    "$MATRIX_PY" -m pip install "$DRIVER_DIR"
  else
    make -C "$DRIVER_DIR" install-python PYTHON="$MATRIX_PY"
  fi
  "$MATRIX_PY" -c 'from rgbmatrix import RGBMatrix, RGBMatrixOptions; print("RGBMatrix bindings verified")'
  echo "Physical driver installed. Hardware output integration into the runtime is still required."
  fi
fi
mkdir -p "$(dirname "$OUTPUT_FILE")"
printf '%s\\n' "$OUTPUT_MODE" > "$OUTPUT_FILE"

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
echo "Selected output: $OUTPUT_MODE"
echo "Note: physical driver installation does not yet connect the running web service to the panel."
