"""The frame inspector, driven by the operator's trace selection."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from peaklive.analysis.trace import DECODE_CONFLICT, DECODE_DECODED, TraceRecord
from peaklive.i18n import translate


class InspectorPanel(QWidget):
    """Describes the selected trace row: identity, payload, and decoded signals.

    It reads only from the selection. Incoming frames never overwrite it, so the
    row an operator is studying stays on screen while the bus keeps talking.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.body = QLabel(translate("inspector.empty"), objectName="inspectorBody")
        self.body.setAccessibleName(translate("inspector.accessible"))
        self.body.setWordWrap(True)
        self.body.setTextInteractionFlags(
            self.body.textInteractionFlags().TextSelectableByMouse
            | self.body.textInteractionFlags().TextSelectableByKeyboard
        )
        layout.addWidget(self.body)
        layout.addStretch(1)

    def clear(self) -> None:
        self.body.setText(translate("inspector.empty"))

    def show_record(self, record: TraceRecord | None) -> None:
        if record is None:
            self.clear()
            return
        self.body.setText(
            _render_event(record) if record.event is not None else _render_frame(record)
        )

    # Kept for the older tests and for callers that only have text.
    def text(self) -> str:
        return self.body.text()


def _render_frame(record: TraceRecord) -> str:
    frame = record.frame
    assert frame is not None
    extended = translate("inspector.extended") if frame.is_extended_id else (
        translate("inspector.standard")
    )
    lines = [
        translate("inspector.frame_heading").upper(),
        f"{translate('inspector.timestamp')}: {record.timestamp:.6f} s",
        f"{translate('inspector.arbitration_id')}: 0x{frame.arbitration_id:03X} ({extended})",
        f"{translate('inspector.dlc')}: {frame.dlc}",
        f"{translate('inspector.channel')}: {record.channel}",
        f"{translate('inspector.direction')}: {record.direction}",
    ]
    if frame.is_remote_frame:
        lines.append(translate("inspector.remote"))
    payload = frame.data
    if payload:
        lines.append(f"{translate('inspector.payload')}: {payload.hex(' ').upper()}")
        lines.append(
            f"{translate('inspector.payload_bytes')}: "
            + ", ".join(f"[{index}] 0x{byte:02X} ({byte})" for index, byte in enumerate(payload))
        )
    else:
        lines.append(f"{translate('inspector.payload')}: {translate('inspector.payload_empty')}")
    lines.append("")
    if record.message_name:
        lines.append(f"{translate('inspector.message')}: {record.message_name}")
    lines.append(f"{translate('inspector.decode_status')}: {record.decode_status}")
    if record.signals:
        database = record.signals[0].database_hash[:8]
        lines.append(f"{translate('inspector.database')}: {database}")
        lines.append(translate("inspector.signals").upper())
        for signal in record.signals:
            unit = f" {signal.unit}" if signal.unit else ""
            lines.append(f"  {signal.signal_name} = {signal.value}{unit}")
    else:
        reason = (
            translate("inspector.reason_conflict")
            if record.decode_status == DECODE_CONFLICT
            else translate("inspector.reason_unknown")
        )
        if record.decode_status != DECODE_DECODED:
            lines.append(translate("inspector.no_signals").format(reason=reason))
    return "\n".join(lines)


def _render_event(record: TraceRecord) -> str:
    event = record.event
    assert event is not None
    return "\n".join(
        (
            translate("inspector.event_heading").upper(),
            f"{translate('inspector.timestamp')}: {record.timestamp:.6f} s",
            f"{translate('inspector.event_kind')}: {event.kind}",
            f"{translate('inspector.channel')}: {record.channel}",
            f"{translate('inspector.event_message')}: {event.message}",
        )
    )
