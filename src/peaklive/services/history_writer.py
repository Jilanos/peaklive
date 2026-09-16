"""Bounded single-writer ownership for historical signal persistence.

Historical sample/summary/run-event writes used to happen synchronously on
the GUI thread, inside the same Qt slot that drains a replay batch or an
acquisition frame batch. That is the single dominant cost of loading a dense
capture (see the trace-loading audit), and it blocks the interaction budget
for as long as SQLite needs to append, maintain seven summary levels and
commit. `HistoryWriter` moves all of that off the GUI thread behind one
owner: frame/series/trace projection stays synchronous (it is comparatively
cheap and the trace/series in-memory stores are not thread-safe for
concurrent writers), but the SQL work is hand off to this thread and
acknowledged through the same bounded backpressure contract `ReplayWorker`
already uses for its own batches.
"""

from __future__ import annotations

import shutil
import sqlite3
from collections.abc import Callable
from pathlib import Path
from queue import Empty, Full, Queue
from threading import Event
from time import perf_counter
from typing import Any

from PySide6.QtCore import QThread, Signal

from peaklive.analysis.history import HistoricalSignalStore
from peaklive.analysis.profiling import PROFILER, STAGE_HISTORY_WRITE, STAGE_QUEUE_WAIT
from peaklive.diagnostics import logger

#: How many accepted-but-not-yet-persisted batches may queue at once. Kept in
#: the same order of magnitude as `ReplayWorker.MAX_PENDING_BATCHES`: enough
#: that a momentarily slower disk does not stall ingestion, not so many that
#: an unbounded amount of unpersisted history can accumulate in RAM.
MAX_QUEUE_BATCHES = 8

#: How long `submit()` waits for queue room before checking for a stop/fail.
QUEUE_POLL_TIMEOUT_S = 0.25

#: Bound on continuous backpressure before `submit()` reports failure. A
#: writer that cannot drain its queue for this long is failed the same way
#: an unresponsive replay presentation consumer is: explicitly, not silently.
QUEUE_STALL_TIMEOUT_S = 5.0

#: Free-space margin the writer refuses to write below. Historical storage
#: has been measured to reach roughly 39x the synthetic source bytes for a
#: dense multi-signal capture; refusing near-exhaustion explicitly is safer
#: than letting SQLite fail mid-commit with an opaque disk-full error.
MIN_FREE_DISK_BYTES = 64 * 1024 * 1024

#: How long this thread's own SQLite connection retries a lock conflict
#: before raising. sqlite3's own default is 5s; a lock held that long is
#: itself worth surfacing as an explicit failure rather than a silent stall
#: that leaves the queue not draining with no visible cause.
WRITE_LOCK_TIMEOUT_S = 1.0

HistoricalSample = tuple[str, float, Any, str | None]


class HistoryWriteRefused(RuntimeError):
    """Raised internally when disk admission refuses a write before it starts."""


class HistoryWriter(QThread):
    """Owns the one write connection to a session's `HistoricalSignalStore`.

    A producer (the GUI thread) only ever calls `submit()`; every SQLite
    append, summary/run-event maintenance and commit happens on this thread.
    `submit()` is the single backpressure point, blocking the caller with a
    bounded stall budget rather than letting the queue grow without limit -
    the same shape as `ReplayWorker._dispatch`'s permit wait.
    """

    #: Emitted from this thread when a write is refused or raises; the GUI
    #: connects it to the same failure containment `_ingest_frames` already
    #: uses for a synchronous write (item_132), so both paths converge on one
    #: explicit terminal state instead of two different failure contracts.
    write_failed = Signal(str)
    #: Emitted after each batch is durably committed, carrying the number of
    #: samples persisted - the "ready" milestone lags "accepted" by however
    #: long the queue takes to drain.
    settled = Signal(int)

    def __init__(
        self,
        path: Path,
        *,
        on_ready: Callable[[HistoricalSignalStore], None] | None = None,
    ) -> None:
        super().__init__()
        self._path = path
        # Runs on this thread, right after the store opens and before the
        # first queued batch: the only place test code can safely reach the
        # write connection (sqlite3 forbids cross-thread use of one
        # connection object). Production callers never pass this.
        self._on_ready = on_ready
        self._queue: Queue[list[HistoricalSample] | None] = Queue(maxsize=MAX_QUEUE_BATCHES)
        self._stop_requested = Event()
        self._failed = Event()
        #: Set just before `write_failed` is emitted, so a caller whose
        #: `submit()` lost the race with the not-yet-delivered queued signal
        #: can still read the real cause synchronously instead of only a
        #: generic backpressure message.
        self.last_error: str | None = None
        #: The store this thread owns, set once `run()` has opened it. Public
        #: only so a test can wait for it and inspect the write connection
        #: directly; production code has no reason to reach into it.
        self.store: HistoricalSignalStore | None = None

    def request_stop(self) -> None:
        """Ask the writer to finish already-queued batches, then exit.

        A pending `submit()` call unblocks as soon as this is observed rather
        than waiting out its full stall budget.
        """
        self._stop_requested.set()

    @property
    def failed(self) -> bool:
        return self._failed.is_set()

    def submit(self, batch: list[HistoricalSample]) -> bool:
        """Hand one batch to the writer, waiting while its queue is full.

        Returns False if the batch could not be accepted within the bounded
        stall budget - a full queue for too long, or a writer that has
        already failed or been asked to stop. The caller must treat that
        exactly like a synchronous persistence failure.
        """
        if self._failed.is_set() or self._stop_requested.is_set():
            return False
        with PROFILER.stage(STAGE_QUEUE_WAIT):
            stalled_since = perf_counter()
            while True:
                try:
                    self._queue.put(batch, timeout=QUEUE_POLL_TIMEOUT_S)
                    return True
                except Full:
                    if self._failed.is_set() or self._stop_requested.is_set():
                        return False
                    if perf_counter() - stalled_since >= QUEUE_STALL_TIMEOUT_S:
                        return False

    def pending(self) -> int:
        """Return the exact number of batches accepted but not yet settled."""
        return self._queue.qsize()

    def has_room(self) -> bool:
        """Whether `submit()` would return without waiting for queue room.

        The GUI thread is the only producer, so a caller that sees room here
        can submit one batch without blocking its event loop. A failed or
        stopping writer also reports room: `submit()` refuses it immediately,
        and that refusal is the caller's failure signal, not a stall.
        """
        return self._failed.is_set() or self._stop_requested.is_set() or not self._queue.full()

    def run(self) -> None:
        try:
            store = HistoricalSignalStore(self._path, timeout=WRITE_LOCK_TIMEOUT_S)
        except sqlite3.Error as error:
            self._fail(error)
            return
        self.store = store
        if self._on_ready is not None:
            self._on_ready(store)
        try:
            while True:
                try:
                    batch = self._queue.get(timeout=QUEUE_POLL_TIMEOUT_S)
                except Empty:
                    if self._stop_requested.is_set():
                        return
                    continue
                if batch is None:
                    return
                try:
                    self._admit_or_refuse()
                    with PROFILER.stage(STAGE_HISTORY_WRITE):
                        count = store.append_many(batch)
                except (sqlite3.Error, HistoryWriteRefused) as error:
                    self._fail(error)
                    return
                self.settled.emit(count)
        finally:
            store.close()

    def _fail(self, error: Exception) -> None:
        logger().exception("history write failed: %s", error)
        self.last_error = str(error)
        self._failed.set()
        self.write_failed.emit(str(error))

    def _admit_or_refuse(self) -> None:
        usage = shutil.disk_usage(self._path.parent)
        if usage.free < MIN_FREE_DISK_BYTES:
            raise HistoryWriteRefused(
                f"Only {usage.free} byte(s) free on the historical storage volume; "
                f"the configured minimum is {MIN_FREE_DISK_BYTES}."
            )
