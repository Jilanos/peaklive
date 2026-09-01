"""Background replay of large traces without loading the capture into memory."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from threading import Event, Lock, Semaphore
from time import perf_counter

from PySide6.QtCore import QThread, Signal

from peaklive.analysis import iter_trace
from peaklive.analysis.profiling import PROFILER, STAGE_DISPATCH, STAGE_PARSE
from peaklive.analysis.replay import TraceCursor
from peaklive.domain import BusEvent, CanFrame

#: How many frames one presentation notification carries.
BATCH_SIZE = 256

#: The shortest interval between two progress notifications. Progress is a
#: reassurance, not a measurement, and emitting one per batch floods the UI
#: thread's event queue on a fast disk.
PROGRESS_INTERVAL_S = 0.05

#: How many dispatched batches may be waiting for the UI thread at once.
#:
#: Parsing is far faster than presenting, so without a bound the worker queues
#: thousands of batches and one event-loop pass has to render all of them. Stop
#: and every other user action then sit behind that pass. Holding the parser to
#: a few batches ahead is what keeps a single pass short enough to stay inside
#: the responsiveness budget.
MAX_PENDING_BATCHES = 4

#: How long the parser waits for the UI to acknowledge before checking whether
#: it has been asked to stop. A worker whose generation was abandoned never
#: receives another acknowledgement, so the wait must never be unbounded.
ACKNOWLEDGEMENT_TIMEOUT_S = 0.25


class ReplayWorker(QThread):
    """Read ASC/TRC records incrementally and batch presentation notifications."""

    frames_received = Signal(list)
    event_received = Signal(object)
    replay_failed = Signal(str)
    # done/total are source bytes, allowing truthful monotonic progress without
    # preloading or counting records.
    progressed = Signal(int, int)

    def __init__(self, path: Path) -> None:
        super().__init__()
        self._path = path
        self._stop_requested = Event()
        self._cursor = TraceCursor()
        self._pending_batches = Semaphore(MAX_PENDING_BATCHES)
        self._permit_lock = Lock()
        self._held_permits = 0
        self._last_progress = 0
        self._last_progress_at = 0.0

    def request_stop(self) -> None:
        self._stop_requested.set()

    def batch_rendered(self) -> None:
        """Report from the UI thread that one dispatched batch has landed."""
        with self._permit_lock:
            if not self._held_permits:
                return
            self._held_permits -= 1
        self._pending_batches.release()

    @property
    def pending_batch_count(self) -> int:
        """Return the exact number of dispatched, unrendered batches."""
        with self._permit_lock:
            return self._held_permits

    def run(self) -> None:
        batch: list[CanFrame] = []
        anomalies: Counter[str] = Counter()
        try:
            total = self._path.stat().st_size
            records = PROFILER.timed_iter(
                STAGE_PARSE, iter_trace(self._path, self._cursor)
            )
            for record in records:
                if self._stop_requested.is_set():
                    break
                if isinstance(record, BusEvent):
                    if record.kind == "replay_anomaly":
                        anomalies[record.message] += 1
                    else:
                        self.event_received.emit(record)
                    continue
                batch.append(record)
                if len(batch) >= BATCH_SIZE:
                    if not self._dispatch(batch):
                        break
                    batch = []
                self._emit_progress(total)
            if batch:
                self._dispatch(batch)
            for message, count in anomalies.items():
                suffix = f" ({count} occurrences)" if count > 1 else ""
                self.event_received.emit(BusEvent(0.0, "replay_anomaly", message + suffix))
            self.progressed.emit(total, total)
        except OSError as error:
            self.replay_failed.emit(str(error))

    def _dispatch(self, batch: list[CanFrame]) -> bool:
        """Hand one batch to the UI, waiting if it is already several behind.

        The wait is deliberately outside the measured stage: time spent held
        back by the display is the display's cost, and attributing it to
        dispatch would hide the stage that actually caused it.
        """
        if not self._pending_batches.acquire(timeout=ACKNOWLEDGEMENT_TIMEOUT_S):
            # Never emit a batch without a permit: doing so turns its eventual
            # acknowledgement into a new permit and removes the bound.
            return False
        with self._permit_lock:
            self._held_permits += 1
        with PROFILER.stage(STAGE_DISPATCH):
            PROFILER.count_frames(len(batch))
            self.frames_received.emit(batch)
        return True

    def _emit_progress(self, total: int) -> None:
        """Report parse progress from consumed source bytes, never from the file.

        The file's own size is constant during a replay, so asking for it again
        would report completion from the first batch onwards. The parser's
        cursor is the only signal that actually advances.
        """
        if total <= 0:
            return
        done = min(self._cursor.consumed, total)
        if done <= self._last_progress:
            return
        now = perf_counter()
        if now - self._last_progress_at < PROGRESS_INTERVAL_S:
            return
        self._last_progress = done
        self._last_progress_at = now
        self.progressed.emit(done, total)
