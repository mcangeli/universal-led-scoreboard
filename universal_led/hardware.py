"""Hardware target detection, with no GPIO or third-party imports."""
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class HardwareInfo:
    model: str
    os_name: str
    os_version: str
    matrix_driver: str = 'emulator'

def detect_model(path: str = '/proc/device-tree/model') -> str:
    try:
        return Path(path).read_bytes().decode('utf-8', errors='replace').strip('\x00\n ')
    except OSError:
        return 'Unknown hardware'

def detect_os(path: str = '/etc/os-release') -> tuple[str, str]:
    try:
        values = {}
        for line in Path(path).read_text().splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                values[key] = value.strip('"')
        return values.get('NAME', 'Unknown OS'), values.get('VERSION_CODENAME', 'unknown')
    except OSError:
        return 'Unknown OS', 'unknown'

def detect_hardware() -> HardwareInfo:
    name, version = detect_os()
    return HardwareInfo(detect_model(), name, version)

def physical_driver_warning(info: HardwareInfo) -> str:
    if 'Raspberry Pi 5' in info.model:
        return 'Pi 5 physical HUB75 output requires a separately validated compatible driver.'
    return 'Physical HUB75 output is not implemented yet; use emulator mode.'
