"""Privacy-preserving runtime metrics for the packaged black-box qualifier.

Only aggregate counters and lifecycle state are persisted.  This module must
never receive a CAN frame, identifier, payload, signal, or DBC object.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from time import monotonic


class QualificationMetrics:
    """Append bounded, payload-blind aggregate samples when explicitly enabled."""

    def __init__(self, path: Path, interval: float = 1.0) -> None:
        self._path = path
        self._interval = max(0.1, interval)
        self._lock = threading.Lock()
        self._started = monotonic()
        self._last_write = 0.0
        self._frames = 0
        self._events = 0
        self._errors = 0
        self._state = "starting"
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_environment(cls) -> QualificationMetrics | None:
        configured = os.environ.get("PEAKLIVE_QUALIFICATION_METRICS")
        return cls(Path(configured)) if configured else None

    def record(
        self,
        *,
        state: str | None = None,
        frames: int = 0,
        events: int = 0,
        errors: int = 0,
        force: bool = False,
    ) -> None:
        """Record aggregate deltas, writing at most once per configured interval."""
        with self._lock:
            self._frames += max(0, frames)
            self._events += max(0, events)
            self._errors += max(0, errors)
            if state is not None:
                self._state = state
            now = monotonic()
            if not force and now - self._last_write < self._interval:
                return
            payload = {
                "elapsed_s": round(now - self._started, 3),
                "state": self._state,
                "frames": self._frames,
                "events": self._events,
                "errors": self._errors,
            }
            with self._path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(payload, separators=(",", ":")) + "\n")
            self._last_write = now

    def close(self, state: str = "stopped") -> None:
        self.record(state=state, force=True)


def metrics_for_environment() -> QualificationMetrics | None:
    """Return the optional writer used by worker code and tests."""
    return QualificationMetrics.from_environment()

