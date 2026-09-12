"""Deriving a newly selected signal from the session that is already loaded.

A session decodes only the signals that were selected while it ingested, so a
signal chosen afterwards has nothing to plot. Reopening the capture would
reparse every frame, discard the operator's state, and take exactly as long as
the load the audit just made faster. Instead the bounded frame cache is decoded
again for the one signal that was asked for — off the UI thread, against a
snapshot, and always as a whole series rather than an append, so selecting the
same signal twice produces the same samples rather than twice as many.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from threading import Event
from typing import Any

from PySide6.QtCore import QThread, Signal

from peaklive.analysis import AmbiguousMessageError, DbcCatalog, HistoricalSignalStore, iter_trace
from peaklive.domain import BusEvent, CanFrame

#: How many cached frames one cancellation check covers. Small enough that a
#: cancelled or superseded request stops promptly, large enough that the check
#: is not itself a measurable share of the decode.
CANCEL_CHECK_INTERVAL = 2_048
SOURCE_BATCH_SIZE = 4_096
SOURCE_TAIL_SAMPLES = 20_000


@dataclass(frozen=True, slots=True)
class DecodedSeries:
    """Everything the commit needs to install one backfilled signal."""

    signal_name: str
    samples: tuple[tuple[float, Any], ...]
    unit: str | None
    #: How many frames the cache had ingested when the snapshot was taken, so
    #: the commit can decode exactly the frames that arrived after it.
    ingested: int
    #: Whether the retention bound had already dropped part of the session.
    truncated: bool
    #: Complete source-backed count when the worker streamed a capture file.
    source_count: int | None = None

    @property
    def is_empty(self) -> bool:
        return not self.samples


def decode_series(
    catalog: DbcCatalog,
    frames: tuple[CanFrame, ...],
    signal_name: str,
) -> tuple[tuple[float, Any], ...]:
    """Decode `signal_name` out of `frames`, skipping frames that lack it."""
    samples: list[tuple[float, Any]] = []
    for frame in frames:
        try:
            decoded = catalog.decode(frame)
        except (AmbiguousMessageError, ValueError, TypeError, KeyError):
            # An unresolved conflict is reported by the live decode path; a
            # backfill must not turn it into a second, duplicate complaint.
            continue
        for signal in decoded:
            if signal.signal_key == signal_name or signal.display_name == signal_name:
                samples.append((frame.timestamp, signal.value))
    return tuple(samples)


def signal_unit(catalog: DbcCatalog, signal_name: str) -> str | None:
    for reference in catalog.signal_references():
        if reference.signal_key == signal_name or reference.display_name == signal_name:
            return reference.unit
    return None


class SignalDecodeWorker(QThread):
    """Decode one signal out of a retained frame snapshot, off the UI thread."""

    completed = Signal(object)
    cancelled = Signal()

    def __init__(
        self,
        catalog: DbcCatalog,
        frames: tuple[CanFrame, ...],
        signal_name: str,
        ingested: int,
        *,
        truncated: bool = False,
        generation: int = 0,
    ) -> None:
        super().__init__()
        # Copied on the calling thread, like every other prepared catalog
        # operation, so the worker cannot read a catalog being mutated.
        self._catalog = catalog.copy()
        self._frames = frames
        self._signal_name = signal_name
        self._ingested = ingested
        self._truncated = truncated
        self._generation = generation
        self._cancel_requested = Event()

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def signal_name(self) -> str:
        return self._signal_name

    def request_cancel(self) -> None:
        self._cancel_requested.set()

    def run(self) -> None:
        samples: list[tuple[float, Any]] = []
        for start in range(0, len(self._frames), CANCEL_CHECK_INTERVAL):
            if self._cancel_requested.is_set():
                self.cancelled.emit()
                return
            chunk = self._frames[start : start + CANCEL_CHECK_INTERVAL]
            samples.extend(decode_series(self._catalog, chunk, self._signal_name))
        if self._cancel_requested.is_set():
            self.cancelled.emit()
            return
        self.completed.emit(
            DecodedSeries(
                self._signal_name,
                tuple(samples),
                signal_unit(self._catalog, self._signal_name),
                self._ingested,
                self._truncated,
            )
        )


class SourceSignalDecodeWorker(QThread):
    """Decode one signal from the full opened capture into the history store."""

    completed = Signal(object)
    cancelled = Signal(int)
    failed = Signal(str, int)
    progressed = Signal(int, int, int)

    def __init__(
        self,
        catalog: DbcCatalog,
        source_path: Path,
        history_path: Path,
        signal_name: str,
        generation: int,
        *,
        tail_limit: int = SOURCE_TAIL_SAMPLES,
    ) -> None:
        super().__init__()
        self._catalog = catalog.copy()
        self._source_path = source_path
        self._history_path = history_path
        self._signal_name = signal_name
        self._generation = generation
        self._tail_limit = tail_limit
        self._cancel_requested = Event()
        stat = source_path.stat()
        self._source_size = stat.st_size
        self._source_mtime_ns = stat.st_mtime_ns

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def signal_name(self) -> str:
        return self._signal_name

    def request_cancel(self) -> None:
        self._cancel_requested.set()

    def run(self) -> None:
        count = 0
        tail: deque[tuple[float, Any]] = deque(maxlen=self._tail_limit)
        batch: list[tuple[str, float, Any, str | None]] = []
        try:
            with HistoricalSignalStore(self._history_path) as history:
                history.drop_signal(self._signal_name)
                for record in iter_trace(self._source_path):
                    if self._cancel_requested.is_set():
                        history.drop_signal(self._signal_name)
                        self.cancelled.emit(self._generation)
                        return
                    if isinstance(record, BusEvent):
                        continue
                    try:
                        decoded = self._catalog.decode(record)
                    except (AmbiguousMessageError, ValueError, TypeError, KeyError):
                        continue
                    for signal in decoded:
                        if (
                            signal.signal_key != self._signal_name
                            and signal.display_name != self._signal_name
                        ):
                            continue
                        sample = (record.timestamp, signal.value)
                        batch.append(
                            (
                                self._signal_name,
                                record.timestamp,
                                signal.value,
                                signal.unit,
                            )
                        )
                        tail.append(sample)
                        count += 1
                    if len(batch) >= SOURCE_BATCH_SIZE:
                        history.append_many(batch)
                        batch.clear()
                        self.progressed.emit(count, self._source_size, self._generation)
                if batch:
                    history.append_many(batch)
            self._raise_if_source_changed()
        except Exception as error:
            self._cleanup_partial_history()
            if not self._cancel_requested.is_set():
                self.failed.emit(str(error), self._generation)
            return
        if self._cancel_requested.is_set():
            self._cleanup_partial_history()
            self.cancelled.emit(self._generation)
            return
        self.completed.emit(
            DecodedSeries(
                self._signal_name,
                tuple(tail),
                signal_unit(self._catalog, self._signal_name),
                0,
                False,
                count,
            )
        )

    def _raise_if_source_changed(self) -> None:
        stat = self._source_path.stat()
        if stat.st_size != self._source_size or stat.st_mtime_ns != self._source_mtime_ns:
            raise RuntimeError("Source capture changed during signal reconstruction")

    def _cleanup_partial_history(self) -> None:
        try:
            with HistoricalSignalStore(self._history_path) as history:
                history.drop_signal(self._signal_name)
        except Exception:
            pass
