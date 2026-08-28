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

from dataclasses import dataclass
from threading import Event
from typing import Any

from PySide6.QtCore import QThread, Signal

from peaklive.analysis import AmbiguousMessageError, DbcCatalog
from peaklive.domain import CanFrame

#: How many cached frames one cancellation check covers. Small enough that a
#: cancelled or superseded request stops promptly, large enough that the check
#: is not itself a measurable share of the decode.
CANCEL_CHECK_INTERVAL = 2_048


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

    @property
    def is_empty(self) -> bool:
        return not self.samples


def decode_series(
    catalog: DbcCatalog,
    frames: tuple[CanFrame, ...],
    signal_name: str,
) -> tuple[tuple[float, Any], ...]:
    """Decode `signal_name` out of `frames`, skipping frames that lack it."""
    message_name, _, plain_name = signal_name.partition(".")
    samples: list[tuple[float, Any]] = []
    for frame in frames:
        try:
            decoded = catalog.decode(frame)
        except AmbiguousMessageError:
            # An unresolved conflict is reported by the live decode path; a
            # backfill must not turn it into a second, duplicate complaint.
            continue
        for signal in decoded:
            if signal.message_name == message_name and signal.signal_name == plain_name:
                samples.append((frame.timestamp, signal.value))
    return tuple(samples)


def signal_unit(catalog: DbcCatalog, signal_name: str) -> str | None:
    message_name, _, plain_name = signal_name.partition(".")
    for reference in catalog.signal_references():
        if reference.message_name == message_name and reference.signal_name == plain_name:
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
