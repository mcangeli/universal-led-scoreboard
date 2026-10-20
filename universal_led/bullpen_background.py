"""Thread-safe Bullpen data refresh and cached framebuffer rendering.

A single worker performs potentially blocking plugin updates. The display
thread only reads the last completed framebuffer, never plugin mutable state.
"""
from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from .bullpen_screen import BullpenScreen
from .display import Framebuffer

LOG = logging.getLogger(__name__)


class BullpenBackgroundScreen:
    def __init__(self, screen: BullpenScreen):
        self.screen = screen
        self._lock = threading.Lock()
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="uls-bullpen")
        self._future = None
        self._frame: Optional[Framebuffer] = None
        self._closed = False

    def refresh(self) -> bool:
        """Schedule one refresh, coalescing calls while a refresh is running."""
        with self._lock:
            if self._closed:
                return False
            if self._future is not None and not self._future.done():
                return False
            self._future = self._worker.submit(self._refresh_once)
            return True

    def _refresh_once(self) -> None:
        try:
            # Plugin state is only accessed from the worker. Do not hold
            # _lock while invoking plugin code or network requests.
            status = self.screen.data.update()
            if hasattr(status, "ok") and not status.ok():
                return
            frame = self.screen.render_cached()
            with self._lock:
                if not self._closed:
                    self._frame = frame
        except Exception:
            LOG.exception("Bullpen background refresh failed")

    def render(self) -> Optional[Framebuffer]:
        """Return last completed frame immediately; never wait for network."""
        with self._lock:
            return self._frame

    def reset(self) -> None:
        # A reset must not race plugin rendering on the worker.
        with self._lock:
            if self._closed:
                return
            self._frame = None
        self.refresh()

    def close(self) -> None:
        with self._lock:
            self._closed = True
            self._frame = None
        self._worker.shutdown(wait=False, cancel_futures=True)
