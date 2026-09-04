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

#: A defensive cap on distinct anomaly messages tracked per replay. Every
#: anomaly source in `iter_trace` uses a small, static vocabulary, so this
#: should never bind in practice; it exists so a future anomaly message that
#: accidentally carries per-record detail cannot grow this Counter or the
#: drained event count without a hard ceiling.
MAX_ANOMALY_KEYS = 64

#: How many records `iter_trace` must produce before the anomaly ratio is
#: judged. A short, mostly-broken file is common (an operator stopped a
#: capture mid-line); a judgement made too early on it would reject
#: legitimate small traces.
IMPLAUSIBLE_INPUT_MIN_RECORDS = 500

#: Once judged, this fraction of anomalies marks the input as not actually a
#: supported trace - binary data, or the wrong file entirely - rather than a
#: real capture with a few malformed lines.
IMPLAUSIBLE_INPUT_ANOMALY_RATIO = 0.95


class ImplausibleTraceError(RuntimeError):
    """Raised when parsed input looks like it is not a supported trace at all."""


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
        self._succeeded = False

    @property
    def succeeded(self) -> bool:
        """Whether `run()` reached completion without an unhandled failure.

        `finished` fires whenever the thread returns, success or not, so a
        caller that wants to know the difference must check this rather than
        assume completion from `finished` alone.
        """
        return self._succeeded

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
        record_count = 0
        anomaly_count = 0
        try:
            total = self._path.stat().st_size
            records = PROFILER.timed_iter(
                STAGE_PARSE, iter_trace(self._path, self._cursor)
            )
            for record in records:
                if self._stop_requested.is_set():
                    break
                record_count += 1
                if isinstance(record, BusEvent):
                    if record.kind == "replay_anomaly":
                        anomaly_count += 1
                        if len(anomalies) < MAX_ANOMALY_KEYS or record.message in anomalies:
                            anomalies[record.message] += 1
                        self._reject_if_implausible(record_count, anomaly_count)
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
            self._succeeded = True
        except Exception as error:
            self.replay_failed.emit(str(error))

    def _reject_if_implausible(self, record_count: int, anomaly_count: int) -> None:
        """Abort a file that is overwhelmingly unparseable rather than replay it.

        Judged only once enough records have been seen, and only against a
        generous ratio, so a real capture with a handful of malformed lines
        is never mistaken for binary-like or wrong-format input.
        """
        if record_count < IMPLAUSIBLE_INPUT_MIN_RECORDS:
            return
        if anomaly_count / record_count < IMPLAUSIBLE_INPUT_ANOMALY_RATIO:
            return
        raise ImplausibleTraceError(
            f"{self._path.name} does not look like a supported trace: "
            f"{anomaly_count} of the first {record_count} records were unparseable."
        )

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
