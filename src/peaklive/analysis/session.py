"""Bounded session fact collection behind the diagnostic report."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from peaklive.domain import BusEvent, CanFrame

MAX_TRACKED_IDS = 512
ANOMALY_KINDS = {
    "replay_anomaly": "Malformed replay records",
    "error_frame": "Bus error frames",
    "bus_status": "Bus status changes",
    "trc_event": "TRC events",
    "recording_warning": "Recording warnings",
    "dbc_conflict": "DBC conflicts",
    "dbc_error": "DBC load errors",
    "unknown_id": "Unknown arbitration IDs",
}


@dataclass(frozen=True, slots=True)
class DbcSummary:
    """One loaded DBC as it appears in the report."""

    name: str
    short_hash: str
    enabled: bool
    signal_count: int
    resolved_ids: tuple[int, ...] = ()


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
    top_arbitration_ids: tuple[tuple[int, int], ...]
    anomalies: tuple[tuple[str, int], ...]
    tracked_id_count: int
    truncated_ids: bool

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
        self._ids: Counter[int] = Counter()
        self._truncated_ids = False
        self._anomalies: Counter[str] = Counter()

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

    def record_frame(self, frame: CanFrame, *, decoded: bool) -> None:
        self._frames += 1
        self._stamp(frame.timestamp)
        if decoded:
            self._decoded += 1
        else:
            self._anomalies["unknown_id"] += 1
        if frame.arbitration_id in self._ids or len(self._ids) < self._max_tracked_ids:
            self._ids[frame.arbitration_id] += 1
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
                ", resolved " + ", ".join(f"0x{item:03X}" for item in summary.resolved_ids)
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
        for arbitration_id, count in report.top_arbitration_ids:
            self.lines.append(f"  0x{arbitration_id:03X}  {count}")
        if report.truncated_ids:
            self.lines.append(
                f"  (per-ID tracking capped at {report.tracked_id_count} distinct IDs)"
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
