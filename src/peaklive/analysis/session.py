"""Bounded session fact collection behind the diagnostic report."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from peaklive.domain import BusEvent, CanFrame

FrameKey = tuple[int, bool]
FrameKeyLike = FrameKey | int

MAX_TRACKED_IDS = 512
ANOMALY_KINDS = {
    "replay_anomaly": "Malformed replay records",
    "error_frame": "Bus error frames",
    "bus_status": "Bus status changes",
    "trc_event": "TRC events",
    "recording_warning": "Recording warnings",
    "dbc_conflict": "DBC conflicts",
    "dbc_error": "DBC load errors",
    "decode_invalid": "Invalid DBC payloads",
    "unknown_id": "Unknown arbitration IDs",
}


@dataclass(frozen=True, slots=True)
class DbcSummary:
    """One loaded DBC as it appears in the report."""

    name: str
    short_hash: str
    enabled: bool
    signal_count: int
    resolved_ids: tuple[FrameKeyLike, ...] = ()


@dataclass(frozen=True, slots=True)
class SessionReport:
    """The rendered synthesis of one acquisition or replay session."""

    source: str
    first_timestamp: float | None
    last_timestamp: float | None
    frame_count: int
    event_count: int
    decoded_count: int
    dbc_summaries: tuple[DbcSummary, ...]
    top_arbitration_ids: tuple[tuple[FrameKey, int], ...]
    anomalies: tuple[tuple[str, int], ...]
    tracked_id_count: int
    truncated_ids: bool
    identifier_aggregates: tuple[IdentifierAggregate, ...] = ()

    @property
    def duration(self) -> float:
        if self.first_timestamp is None or self.last_timestamp is None:
            return 0.0
        return max(0.0, self.last_timestamp - self.first_timestamp)

    @property
    def frames_per_second(self) -> float:
        duration = self.duration
        return self.frame_count / duration if duration > 0 else 0.0

    @property
    def decode_coverage(self) -> float:
        if not self.frame_count:
            return 0.0
        return self.decoded_count / self.frame_count

    @property
    def is_empty(self) -> bool:
        return self.frame_count == 0 and self.event_count == 0


class SessionFacts:
    """Accumulates report facts with a bounded per-ID tracking table."""

    def __init__(self, max_tracked_ids: int = MAX_TRACKED_IDS) -> None:
        self._max_tracked_ids = max_tracked_ids
        self.source = ""
        self._first: float | None = None
        self._last: float | None = None
        self._frames = 0
        self._events = 0
        self._decoded = 0
        self._ids: Counter[FrameKey] = Counter()
        self._truncated_ids = False
        self._anomalies: Counter[str] = Counter()
        self._aggregates: dict[FrameKey, IdentifierAggregate] = {}

    def reset(self, source: str = "") -> None:
        self.source = source
        self._first = None
        self._last = None
        self._frames = 0
        self._events = 0
        self._decoded = 0
        self._ids = Counter()
        self._truncated_ids = False
        self._anomalies = Counter()
        self._aggregates = {}

    def record_frame(self, frame: CanFrame, *, decoded: bool) -> None:
        self._frames += 1
        self._stamp(frame.timestamp)
        if decoded:
            self._decoded += 1
        else:
            self._anomalies["unknown_id"] += 1
        frame_key = frame.identifier_key
        if frame_key in self._ids or len(self._ids) < self._max_tracked_ids:
            self._ids[frame_key] += 1
            aggregate = self._aggregates.get(frame_key)
            if aggregate is None:
                aggregate = IdentifierAggregate(frame_key)
                self._aggregates[frame_key] = aggregate
            aggregate.update(frame, decoded=decoded)
        else:
            self._truncated_ids = True

    def record_event(self, event: BusEvent) -> None:
        self._events += 1
        self._stamp(event.timestamp)
        if event.kind in ANOMALY_KINDS:
            self._anomalies[event.kind] += 1

    def record_anomaly(self, kind: str) -> None:
        self._anomalies[kind] += 1

    def _stamp(self, timestamp: float) -> None:
        if self._first is None or timestamp < self._first:
            self._first = timestamp
        if self._last is None or timestamp > self._last:
            self._last = timestamp

    def report(self, dbc_summaries: tuple[DbcSummary, ...] = (), limit: int = 12) -> SessionReport:
        return SessionReport(
            source=self.source,
            first_timestamp=self._first,
            last_timestamp=self._last,
            frame_count=self._frames,
            event_count=self._events,
            decoded_count=self._decoded,
            dbc_summaries=dbc_summaries,
            top_arbitration_ids=tuple(self._ids.most_common(limit)),
            anomalies=tuple(sorted(self._anomalies.items())),
            tracked_id_count=len(self._ids),
            truncated_ids=self._truncated_ids,
            identifier_aggregates=tuple(
                sorted(
                    self._aggregates.values(),
                    key=lambda item: (-item.count, item.arbitration_id, item.is_extended_id),
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class IdentifierAggregate:
    """A bounded, O(1)-updated diagnostic row for one arbitration ID."""

    frame_key: FrameKey
    latest_frame: CanFrame | None = None
    count: int = 0
    mean_period: float | None = None
    delta_t: float | None = None
    load_contribution: float | None = None
    decode_status: str = "unknown"
    _last_timestamp: float | None = field(default=None, repr=False, compare=False)
    _period_sum: float = field(default=0.0, repr=False, compare=False)
    _period_count: int = field(default=0, repr=False, compare=False)

    @property
    def arbitration_id(self) -> int:
        return self.frame_key[0]

    @property
    def is_extended_id(self) -> bool:
        return self.frame_key[1]

    def update(self, frame: CanFrame, *, decoded: bool, bitrate: int | None = None) -> None:
        """Update this row in constant time; callers retain one row per ID."""
        previous = self._last_timestamp
        interval = None if previous is None else max(0.0, frame.timestamp - previous)
        period_sum = self._period_sum + (interval or 0.0)
        period_count = self._period_count + (interval is not None)
        status = "decoded" if decoded else "unknown"
        if self.count and self.decode_status != status:
            status = "partial"
        object.__setattr__(self, "latest_frame", frame)
        object.__setattr__(self, "count", self.count + 1)
        object.__setattr__(self, "delta_t", interval)
        object.__setattr__(self, "_last_timestamp", frame.timestamp)
        object.__setattr__(self, "_period_sum", period_sum)
        object.__setattr__(self, "_period_count", period_count)
        object.__setattr__(self, "mean_period", period_sum / period_count if period_count else None)
        object.__setattr__(self, "decode_status", status)
        if bitrate and bitrate > 0:
            bits = 47 + (8 * frame.dlc)
            object.__setattr__(
                self,
                "load_contribution",
                bits / max(self.mean_period or 0.0, 1e-12) / bitrate,
            )


class IdentifierDiagnostics:
    """Standalone aggregate model for live and replay views."""

    def __init__(self, max_identifiers: int = MAX_TRACKED_IDS, bitrate: int | None = None) -> None:
        self.max_identifiers = max_identifiers
        self.bitrate = bitrate
        self._rows: dict[FrameKey, IdentifierAggregate] = {}

    def reset(self) -> None:
        self._rows.clear()

    def update(self, frame: CanFrame, *, decoded: bool) -> IdentifierAggregate | None:
        frame_key = frame.identifier_key
        row = self._rows.get(frame_key)
        if row is None:
            if len(self._rows) >= self.max_identifiers:
                return None
            row = IdentifierAggregate(frame_key)
            self._rows[frame_key] = row
        row.update(frame, decoded=decoded, bitrate=self.bitrate)
        return row

    def rows(self) -> tuple[IdentifierAggregate, ...]:
        return tuple(
            sorted(self._rows.values(), key=lambda item: (item.arbitration_id, item.is_extended_id))
        )


@dataclass(slots=True)
class ReportRenderer:
    """Renders a session report as the plain text shown and exported."""

    report: SessionReport
    lines: list[str] = field(default_factory=list)

    def render(self) -> str:
        report = self.report
        self.lines = ["PeakLive session report", ""]
        self._add("Source", report.source or "live acquisition")
        if report.first_timestamp is None:
            self._add("Time range", "no sample captured")
        else:
            self._add(
                "Time range",
                f"{report.first_timestamp:.6f}s to {report.last_timestamp:.6f}s "
                f"({report.duration:.6f}s)",
            )
        self._add("Frames", str(report.frame_count))
        self._add("Events", str(report.event_count))
        self._add("Frames per second", f"{report.frames_per_second:.2f}")
        self._add("Decode coverage", f"{report.decode_coverage * 100:.1f}%")
        self.lines.append("")
        self.lines.append("DBC databases")
        if not report.dbc_summaries:
            self.lines.append("  none loaded")
        for summary in report.dbc_summaries:
            state = "enabled" if summary.enabled else "disabled"
            resolved = (
                ", resolved " + ", ".join(_frame_key_label(item) for item in summary.resolved_ids)
                if summary.resolved_ids
                else ""
            )
            self.lines.append(
                f"  {summary.name} [{summary.short_hash}] {state}, "
                f"{summary.signal_count} signals{resolved}"
            )
        self.lines.append("")
        self.lines.append("Top arbitration IDs")
        if not report.top_arbitration_ids:
            self.lines.append("  no frame captured")
        for frame_key, count in report.top_arbitration_ids:
            self.lines.append(f"  {_frame_key_label(frame_key)}  {count}")
        if report.truncated_ids:
            self.lines.append(
                f"  (per-ID tracking capped at {report.tracked_id_count} distinct IDs)"
            )
        self.lines.append("")
        self.lines.append("Identifier diagnostics")
        if not report.identifier_aggregates:
            self.lines.append("  no identifier captured")
        for row in report.identifier_aggregates:
            latest = row.latest_frame
            latest_text = "-" if latest is None else latest.data.hex(" ").upper()
            period = "-" if row.mean_period is None else f"{row.mean_period:.6f}s"
            delta = "-" if row.delta_t is None else f"{row.delta_t:.6f}s"
            load = "-" if row.load_contribution is None else f"{row.load_contribution * 100:.2f}%"
            self.lines.append(
                f"  {_frame_key_label(row.frame_key)} latest={latest_text} count={row.count} "
                f"mean-period={period} delta-t={delta} load={load} decode={row.decode_status}"
            )
        self.lines.append("")
        self.lines.append("Anomalies")
        if not report.anomalies:
            self.lines.append("  none recorded")
        for kind, count in report.anomalies:
            self.lines.append(f"  {ANOMALY_KINDS.get(kind, kind)}: {count}")
        return "\n".join(self.lines) + "\n"

    def _add(self, label: str, value: str) -> None:
        self.lines.append(f"{label}: {value}")


def _frame_key_label(frame_key: FrameKeyLike) -> str:
    if isinstance(frame_key, int):
        return f"0x{frame_key:03X}"
    arbitration_id, is_extended_id = frame_key
    return f"0x{arbitration_id:03X}{'x' if is_extended_id else ''}"
