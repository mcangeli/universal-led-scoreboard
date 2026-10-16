#!/usr/bin/env bash
# Fresh Raspberry Pi OS Trixie 64-bit system-service bootstrap.
set -Eeuo pipefail
APP=/opt/uls/app
VENV=/opt/uls/venv
CONFIG=/etc/uls
DATA=/var/lib/uls
BRANCH=feature/0.1.0-core-foundation
MODE=emulator
RESUME=0
REPO=https://github.com/mcangeli/universal-led-scoreboard.git
usage() { echo "Usage: bash scripts/install-system.sh [--mode emulator|physical] [--branch BRANCH] [--resume]"; }
while (($#)); do
  case "$1" in
    --resume) RESUME=1; shift ;;
    --mode) (($# >= 2)) || { usage >&2; exit 2; }; MODE="$2"; shift 2 ;;
    --branch) (($# >= 2)) || { usage >&2; exit 2; }; BRANCH="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
[[ "$MODE" == emulator || "$MODE" == physical ]] || { usage >&2; exit 2; }
[[ "$BRANCH" =~ ^[a-zA-Z0-9._/-]+$ ]] || { echo "Invalid branch" >&2; exit 2; }
(( EUID != 0 )) || { echo "Run as a regular sudo-enabled user, not root." >&2; exit 1; }
[[ "$(uname -m)" == aarch64 ]] || { echo "Raspberry Pi OS 64-bit (aarch64) is required." >&2; exit 1; }
[[ -r /etc/os-release ]] || { echo "Cannot identify operating system" >&2; exit 1; }
. /etc/os-release
[[ "${VERSION_CODENAME:-}" == trixie ]] || { echo "Only Raspberry Pi OS Trixie is supported." >&2; exit 1; }
[[ -r /proc/device-tree/model ]] && grep -aq 'Raspberry Pi' /proc/device-tree/model || { echo "A Raspberry Pi is required." >&2; exit 1; }
if (( RESUME )); then
  [[ -d "$APP/.git" && -x "$VENV/bin/python" ]] || { echo "Cannot resume: existing checkout or venv missing." >&2; exit 1; }
  [[ "$(stat -c %U "$APP")" == "$USER" ]] || { echo "Cannot resume: checkout owned by another user." >&2; exit 1; }
  [[ "$(git -C "$APP" branch --show-current)" == "$BRANCH" ]] || { echo "Cannot resume: branch mismatch." >&2; exit 1; }
  [[ -z "$(git -C "$APP" status --porcelain)" ]] || { echo "Cannot resume: checkout has local changes." >&2; exit 1; }
  [[ -f "$CONFIG/secrets/auth.json" || -d "$CONFIG/secrets" ]] || { echo "Cannot resume: configuration directory missing." >&2; exit 1; }
  [[ ! -e /etc/systemd/system/uls-matrix.service || "$MODE" == physical ]] || { echo "Cannot resume physical install as emulator." >&2; exit 1; }
else
  [[ ! -e "$APP" && ! -e /etc/systemd/system/uls-web.service && ! -e /etc/systemd/system/uls-matrix.service ]] || { echo "Existing ULS installation detected. Use --resume for an interrupted installation or sudo ulsctl update for a working installation." >&2; exit 1; }
fi
echo "Installing prerequisites..."
sudo apt-get update
sudo apt-get install -y git curl python3 python3-venv python3-dev python3-pip build-essential sudo
echo "Creating system account and directories..."
id uls >/dev/null 2>&1 || sudo useradd --system --home-dir "$DATA" --shell /usr/sbin/nologin uls
sudo install -d -o "$USER" -g "$(id -gn)" -m 0755 /opt/uls
if (( ! RESUME )); then sudo install -d -o "$USER" -g "$(id -gn)" -m 0755 "$APP"; fi
sudo install -d -o uls -g uls -m 0700 "$CONFIG" "$CONFIG/secrets" "$DATA"
sudo install -d -o uls -g uls -m 0755 /run/uls
echo "Cloning scoreboard..."
if (( ! RESUME )); then
  git clone --branch "$BRANCH" --single-branch "$REPO" "$APP"
  sudo python3 -m venv "$VENV"
  sudo chown -R "$USER:$(id -gn)" "$VENV"
else
  echo "Resuming existing checkout and virtual environment; no clone or venv reset."
fi
"$VENV/bin/python" -m pip install --upgrade pip
echo "Running baseline tests..."
(cd "$APP" && "$VENV/bin/python" -m unittest discover -s tests -p 'test_*.py')
if (( RESUME )); then
  echo "Preserving existing administrator credentials and configuration."
else
  echo "Set administrator password (12 or more characters)."
  sudo chown "$USER:$(id -gn)" "$CONFIG"
  (cd "$APP" && "$VENV/bin/python" -m universal_led.configurator --config-dir "$CONFIG" --set-admin-password)
fi
sudo chown -R uls:uls "$CONFIG" "$DATA"
sudo find "$CONFIG" -type f -exec chmod 0600 {} +
sudo tee /etc/tmpfiles.d/uls.conf >/dev/null <<'EOF'
d /run/uls 0755 uls uls -
EOF
sudo systemd-tmpfiles --create /etc/tmpfiles.d/uls.conf
sudo tee /etc/systemd/system/uls-web.service >/dev/null <<'EOF'
[Unit]
Description=Universal LED Scoreboard Web
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=uls
Group=uls
WorkingDirectory=/opt/uls/app
Environment=HOME=/var/lib/uls
Environment=ULS_FRAME_FILE=/run/uls/live-frame.ppm
ExecStart=/opt/uls/venv/bin/python -m universal_led.configurator --host 0.0.0.0 --port 8080 --config-dir /etc/uls
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
if [[ "$MODE" == physical ]]; then
  echo "Building physical HUB75 driver (this can take several minutes)..."
  sudo apt-get install -y cython3 cmake ninja-build python3-setuptools python3-pil python3-pil.imagetk
  "$VENV/bin/python" -m pip install cython scikit-build-core Pillow setuptools wheel
  mkdir -p "$HOME/.local/src"
  if [[ ! -d "$HOME/.local/src/rpi-rgb-led-matrix/.git" ]]; then
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git "$HOME/.local/src/rpi-rgb-led-matrix"
  fi
  make -C "$HOME/.local/src/rpi-rgb-led-matrix/lib"
  if [[ -f "$HOME/.local/src/rpi-rgb-led-matrix/pyproject.toml" ]]; then
    "$VENV/bin/python" -m pip install --no-build-isolation "$HOME/.local/src/rpi-rgb-led-matrix"
  else
    make -C "$HOME/.local/src/rpi-rgb-led-matrix" install-python PYTHON="$VENV/bin/python"
  fi
  "$VENV/bin/python" -c 'from rgbmatrix import RGBMatrix, RGBMatrixOptions'
  sudo tee /etc/systemd/system/uls-matrix.service >/dev/null <<'EOF'
[Unit]
Description=Universal LED Scoreboard Physical Matrix
After=uls-web.service
Wants=uls-web.service

[Service]
Type=simple
WorkingDirectory=/opt/uls/app
ExecStart=/opt/uls/venv/bin/python -m universal_led.matrix_worker --frame-file /run/uls/live-frame.ppm --mapping adafruit-hat --brightness 40 --gpio-slowdown 4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
fi
sudo install -m 0755 "$APP/scripts/ulsctl" /usr/local/bin/ulsctl
sudo install -m 0755 "$APP/scripts/uls-update" /usr/local/bin/uls-update
sudo bash "$APP/scripts/install-dashboard-restart-helper.sh"
sudo bash "$APP/scripts/install-dashboard-update-helper.sh"
sudo systemctl daemon-reload
sudo systemctl enable --now uls-web.service
if [[ "$MODE" == physical ]]; then sudo systemctl enable --now uls-matrix.service; fi
echo "ULS installation finished. Dashboard: http://$(hostname -I | awk '{print $1}'):8080/"
echo "Check: sudo systemctl status uls-web.service"
if [[ "$MODE" == physical ]]; then echo "Check: sudo ulsctl health"; else echo "Emulator mode: no matrix service was installed."; fi
