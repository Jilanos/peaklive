"""Bounded trace records, display-only filtering, and column value formatting."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field

from peaklive.analysis.dbc import DecodedSignal
from peaklive.domain import (
    TRACE_DECODE_ANY,
    TRACE_DIRECTION_ANY,
    BusEvent,
    CanFrame,
    TraceFilterSettings,
)

DEFAULT_TRACE_CAPACITY = 5_000

DECODE_DECODED = "decoded"
DECODE_UNKNOWN = "unknown"
DECODE_CONFLICT = "conflict"

COLUMN_LABELS: dict[str, str] = {
    "time": "Time",
    "id": "ID",
    "dlc": "DLC",
    "data": "Data",
    "channel": "Channel",
    "direction": "Dir",
    "message": "Message",
    "status": "Status",
}


@dataclass(frozen=True, slots=True)
class TraceRecord:
    """One displayable trace row: a CAN frame or an acquisition event."""

    index: int
    timestamp: float
    kind: str
    direction: str
    channel: str
    frame: CanFrame | None = None
    event: BusEvent | None = None
    message_name: str = ""
    decode_status: str = DECODE_UNKNOWN
    signals: tuple[DecodedSignal, ...] = ()

    @property
    def is_frame(self) -> bool:
        return self.frame is not None

    @property
    def arbitration_id(self) -> int | None:
        return self.frame.arbitration_id if self.frame is not None else None

    @property
    def payload(self) -> bytes:
        return self.frame.data if self.frame is not None else b""

    def signal_names(self) -> tuple[str, ...]:
        return tuple(f"{signal.message_name}.{signal.signal_name}" for signal in self.signals)


class TraceBuffer:
    """A ring buffer of trace records with a constant-time retention policy.

    The previous workspace pruned a QTableWidget row by row, which is quadratic
    under sustained load. A deque with `maxlen` drops the oldest record in
    constant time and never touches the widget while ingesting.
    """

    def __init__(self, capacity: int = DEFAULT_TRACE_CAPACITY) -> None:
        if capacity < 1:
            raise ValueError("A trace buffer needs room for at least one record")
        self._capacity = capacity
        self._records: deque[TraceRecord] = deque(maxlen=capacity)
        self._next_index = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self) -> Iterator[TraceRecord]:
        return iter(self._records)

    def clear(self) -> None:
        self._records.clear()
        self._next_index = 0

    def add_frame(
        self,
        frame: CanFrame,
        *,
        message_name: str = "",
        decode_status: str = DECODE_UNKNOWN,
        signals: Iterable[DecodedSignal] = (),
    ) -> TraceRecord:
        record = TraceRecord(
            index=self._take_index(),
            timestamp=frame.timestamp,
            kind="frame",
            direction="RX",
            channel=frame.channel,
            frame=frame,
            message_name=message_name,
            decode_status=decode_status,
            signals=tuple(signals),
        )
        self._records.append(record)
        return record

    def add_event(self, event: BusEvent) -> TraceRecord:
        record = TraceRecord(
            index=self._take_index(),
            timestamp=event.timestamp,
            kind=event.kind,
            direction="EVENT",
            channel=event.channel,
            event=event,
            decode_status="",
        )
        self._records.append(record)
        return record

    def record(self, index: int) -> TraceRecord | None:
        return next((item for item in self._records if item.index == index), None)

    def _take_index(self) -> int:
        index = self._next_index
        self._next_index += 1
        return index


@dataclass(slots=True)
class FilteredTrace:
    """A filtered projection of the buffer, kept for display only."""

    records: list[TraceRecord] = field(default_factory=list)
    total: int = 0

    @property
    def hidden(self) -> int:
        return max(0, self.total - len(self.records))


def matches(record: TraceRecord, settings: TraceFilterSettings) -> bool:
    """Return whether a record survives the display-only filter set."""
    if record.is_frame and not settings.show_frames:
        return False
    if not record.is_frame and not settings.show_events:
        return False
    if settings.time_start is not None and record.timestamp < settings.time_start:
        return False
    if settings.time_end is not None and record.timestamp > settings.time_end:
        return False
    if settings.direction != TRACE_DIRECTION_ANY:
        if record.direction.casefold() != settings.direction.casefold():
            return False
    if settings.arbitration_id and not _matches_arbitration_id(record, settings.arbitration_id):
        return False
    if settings.message and settings.message.casefold() not in record.message_name.casefold():
        return False
    if settings.signal and not any(
        settings.signal.casefold() in name.casefold() for name in record.signal_names()
    ):
        return False
    if settings.event_kind and settings.event_kind.casefold() not in record.kind.casefold():
        return False
    if settings.decode_status != TRACE_DECODE_ANY:
        # Events carry no decode status, so a decode filter is frame-scoped.
        if not record.is_frame or record.decode_status != settings.decode_status:
            return False
    return True


def filter_records(buffer: TraceBuffer, settings: TraceFilterSettings) -> FilteredTrace:
    total = len(buffer)
    return FilteredTrace([record for record in buffer if matches(record, settings)], total)


def _matches_arbitration_id(record: TraceRecord, query: str) -> bool:
    arbitration_id = record.arbitration_id
    if arbitration_id is None:
        return False
    text = query.strip().casefold().removeprefix("0x")
    if not text:
        return True
    try:
        return arbitration_id == int(text, 16)
    except ValueError:
        return text in f"{arbitration_id:x}"


def cell_text(record: TraceRecord, column_key: str, value_format: str) -> str:
    """Render one trace cell in the operator's chosen format."""
    if column_key == "time":
        return f"{record.timestamp:.6f}" if value_format == "time" else f"{record.timestamp:g}"
    if column_key == "id":
        arbitration_id = record.arbitration_id
        if arbitration_id is None:
            return ""
        suffix = "x" if record.frame is not None and record.frame.is_extended_id else ""
        if value_format == "dec":
            return f"{arbitration_id}{suffix}"
        return f"0x{arbitration_id:03X}{suffix}"
    if column_key == "dlc":
        if record.frame is None:
            return ""
        return f"0x{record.frame.dlc:X}" if value_format == "hex" else str(record.frame.dlc)
    if column_key == "data":
        return _payload_text(record, value_format)
    if column_key == "channel":
        return record.channel
    if column_key == "direction":
        return record.direction
    if column_key == "message":
        if record.event is not None:
            return record.event.message
        return record.message_name
    if column_key == "status":
        return record.kind if record.event is not None else record.decode_status
    return ""


def _payload_text(record: TraceRecord, value_format: str) -> str:
    if record.event is not None:
        return record.event.message
    payload = record.payload
    if value_format == "dec":
        return " ".join(str(byte) for byte in payload)
    if value_format == "bin":
        return " ".join(format(byte, "08b") for byte in payload)
    return payload.hex(" ").upper()
