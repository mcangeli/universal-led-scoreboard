"""Atomic PPM frame handoff between unprivileged renderer and matrix worker."""
from __future__ import annotations
import os
from pathlib import Path
import tempfile
from .display import Framebuffer

def write_frame(path: str | Path, frame: Framebuffer) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".frame-", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(frame.ppm())
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def read_frame(path: str | Path) -> Framebuffer:
    raw = Path(path).read_bytes()
    header = b"P6\n64 32\n255\n"
    if not raw.startswith(header) or len(raw) != len(header) + 64 * 32 * 3:
        raise ValueError("Invalid 64x32 RGB frame")
    frame = Framebuffer()
    data = memoryview(raw)[len(header):]
    for y in range(32):
        for x in range(64):
            i = (y * 64 + x) * 3
            frame.pixels[y][x] = tuple(data[i:i+3])
    return frame
