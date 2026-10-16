#!/usr/bin/env bash
# Rebuild the RGBMatrix Python environment in /opt/uls without changing the
# running worker until the new environment has passed import validation.
set -Eeuo pipefail
[[ $EUID -ne 0 ]] || { echo "Run as the regular installer user." >&2; exit 1; }
UNIT=/etc/systemd/system/uls-matrix.service
[[ -f "$UNIT" ]] || { echo "Matrix systemd unit missing." >&2; exit 1; }
SOURCE="${ULS_DRIVER_SOURCE:-$HOME/.local/src/rpi-rgb-led-matrix}"
[[ -d "$SOURCE" ]] || { echo "Driver source missing: $SOURCE" >&2; exit 1; }
[[ -f "$SOURCE/pyproject.toml" ]] || { echo "Expected upstream root pyproject.toml in $SOURCE" >&2; exit 1; }
if [[ -e /opt/uls/venv ]]; then
  echo "/opt/uls/venv already exists; refusing to overwrite it." >&2
  exit 1
fi
echo "Building independent RGBMatrix environment from $SOURCE..."
sudo install -d -m 0755 /opt/uls/drivers
sudo cp -a "$SOURCE" /opt/uls/drivers/rpi-rgb-led-matrix
sudo python3 -m venv --system-site-packages /opt/uls/venv
sudo /opt/uls/venv/bin/python -m pip install /opt/uls/drivers/rpi-rgb-led-matrix
sudo /opt/uls/venv/bin/python -c 'from rgbmatrix import RGBMatrix, RGBMatrixOptions; print("New RGBMatrix bindings verified")'
echo "The old service has not been modified."
echo "To switch the matrix worker safely, run: bash scripts/switch-matrix-venv.sh"
