"""Bounded live-frame handoff from acquisition workers to the UI thread."""

from __future__ import annotations

from collections.abc import Callable
from threading import Condition, Lock

from PySide6.QtCore import QObject, QThread, QTimer

from peaklive.domain import CanFrame

MAX_LIVE_FRAMES_PER_DRAIN = 256
MAX_PENDING_LIVE_FRAMES = 4096
LIVE_HANDOFF_WAIT_S = 0.25


class LiveFrameHandoff:
    """Queue acquisition frames without posting one Qt event per worker batch."""

    def __init__(
        self,
        owner: QObject,
        render: Callable[[list[CanFrame]], None],
        ready: Callable[[], bool] | None = None,
    ) -> None:
        self._owner = owner
        self._render = render
        # Consulted before a timer-driven drain so a consumer that would have
        # to block - persistence backpressure, in practice - can decline the
        # tick and leave the frames queued instead of stalling the event loop.
        self._ready = ready
        self._lock = Lock()
        self._condition = Condition(self._lock)
        self._generation: int | None = None
        self._pending: list[CanFrame] = []
        self._timer: QTimer | None = None

    def begin(self, generation: int) -> None:
        """Accept only the newest worker generation's visual projection."""
        with self._lock:
            self._generation = generation
            self._pending = []
        if self._timer is None:
            self._timer = QTimer(self._owner)
            self._timer.setInterval(16)
            self._timer.timeout.connect(self.drain)
        self._timer.start()

    def pending(self) -> bool:
        with self._lock:
            return bool(self._pending)

    def count(self) -> int:
        """How many frames are queued but not yet handed to the renderer."""
        with self._lock:
            return len(self._pending)

    def invalidate(self, generation: int) -> None:
        """Discard stale rendering work so lifecycle signals are never queued behind it."""
        with self._lock:
            if self._generation != generation:
                return
            self._generation = None
            self._pending = []
            self._condition.notify_all()
        if self._timer is not None:
            self._timer.stop()

    def queue(self, generation: int, frames: list[CanFrame]) -> None:
        """Queue every worker batch while bounding pending live memory."""
        remaining = frames
        on_ui_thread = QThread.currentThread() is self._owner.thread()
        while remaining:
            with self._lock:
                if self._generation != generation:
                    return
                available = MAX_PENDING_LIVE_FRAMES - len(self._pending)
                if available:
                    accepted = remaining[:available]
                    self._pending.extend(accepted)
                    remaining = remaining[available:]
                    if not remaining:
                        return
                elif not on_ui_thread:
                    self._condition.wait(timeout=LIVE_HANDOFF_WAIT_S)
                    continue
            if on_ui_thread:
                self.drain_now()

    def take(self, limit: int = MAX_LIVE_FRAMES_PER_DRAIN) -> list[CanFrame]:
        """Remove one bounded slice and wake blocked worker-thread producers."""
        with self._lock:
            frames = self._pending[:limit]
            del self._pending[:limit]
            self._condition.notify_all()
        return frames

    def drain(self) -> None:
        """Render one bounded slice, unless the consumer would have to block."""
        if self._ready is not None and not self._ready():
            return
        self.drain_now()

    def drain_now(self) -> None:
        """Render one bounded slice regardless of consumer readiness."""
        frames = self.take()
        if frames:
            self._render(frames)
        if self._timer is not None and self.pending():
            self._timer.start()
