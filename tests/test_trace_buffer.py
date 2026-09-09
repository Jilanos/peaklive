import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QMenu

from peaklive.analysis.dbc import DecodedSignal
from peaklive.analysis.trace import (
    DECODE_DECODED,
    DECODE_UNKNOWN,
    TraceBuffer,
    cell_text,
    filter_records,
    matches,
)
from peaklive.domain import BusEvent, CanFrame, TraceFilterSettings
from peaklive.domain.models import default_trace_columns
from peaklive.ui.panels.trace_view import TraceViewPanel


def _buffer() -> TraceBuffer:
    buffer = TraceBuffer(capacity=10)
    buffer.add_frame(
        CanFrame(1.0, 0x123, b"\x01\x02"),
        message_name="VehicleStatus",
        decode_status=DECODE_DECODED,
        signals=[DecodedSignal("hash", "VehicleStatus", "Speed", 12.5, "km/h")],
    )
    buffer.add_frame(CanFrame(2.0, 0x456, b"\xff"), decode_status=DECODE_UNKNOWN)
    buffer.add_event(BusEvent(3.0, "error_frame", "ErrorFrame"))
    return buffer


def test_buffer_prunes_in_constant_time_without_touching_older_records():
    buffer = TraceBuffer(capacity=3)
    for index in range(100):
        buffer.add_frame(CanFrame(float(index), 0x100 + index, b"\x00"))

    assert len(buffer) == 3
    assert [record.index for record in buffer] == [97, 98, 99]
    assert buffer.record(0) is None
    assert buffer.record(99) is not None


def test_buffer_rejects_a_zero_capacity():
    with pytest.raises(ValueError, match="at least one record"):
        TraceBuffer(capacity=0)


def test_filters_narrow_the_display_without_touching_the_buffer():
    buffer = _buffer()

    only_events = TraceFilterSettings(show_frames=False)
    filtered = filter_records(buffer, only_events)
    assert [record.kind for record in filtered.records] == ["error_frame"]
    assert filtered.total == 3
    assert filtered.hidden == 2
    assert len(buffer) == 3

    by_id = TraceFilterSettings(arbitration_id="0x123")
    assert len(filter_records(buffer, by_id).records) == 1
    assert len(filter_records(buffer, TraceFilterSettings(arbitration_id="123")).records) == 1

    by_message = TraceFilterSettings(message="vehicle")
    assert len(filter_records(buffer, by_message).records) == 1

    by_signal = TraceFilterSettings(signal="speed")
    assert len(filter_records(buffer, by_signal).records) == 1

    by_status = TraceFilterSettings(decode_status=DECODE_UNKNOWN)
    assert len(filter_records(buffer, by_status).records) == 1

    by_event = TraceFilterSettings(event_kind="error")
    assert len(filter_records(buffer, by_event).records) == 1

    by_direction = TraceFilterSettings(direction="rx")
    assert len(filter_records(buffer, by_direction).records) == 2

    by_time = TraceFilterSettings(time_start=2.0, time_end=2.5)
    assert len(filter_records(buffer, by_time).records) == 1


def test_filters_intersect_and_can_produce_an_empty_projection():
    buffer = _buffer()
    settings = TraceFilterSettings(arbitration_id="0x123", decode_status=DECODE_UNKNOWN)

    filtered = filter_records(buffer, settings)

    assert filtered.records == []
    assert filtered.hidden == 3


def test_active_chips_describe_each_filter_and_can_be_cleared_individually():
    settings = TraceFilterSettings(arbitration_id="0x123", show_events=False)

    fields = [field for field, _ in settings.active_chips()]
    assert fields == ["arbitration_id", "show_events"]
    assert settings.is_active()

    settings.reset_field("arbitration_id")
    assert [field for field, _ in settings.active_chips()] == ["show_events"]

    settings.clear()
    assert not settings.is_active()


def test_cell_text_renders_every_supported_format():
    buffer = _buffer()
    frame_record = next(iter(buffer))
    event_record = list(buffer)[-1]

    assert cell_text(frame_record, "time", "time") == "1.000000"
    assert cell_text(frame_record, "id", "hex") == "0x123"
    assert cell_text(frame_record, "id", "dec") == "291"
    assert cell_text(frame_record, "dlc", "dec") == "2"
    assert cell_text(frame_record, "dlc", "hex") == "0x2"
    assert cell_text(frame_record, "data", "hex") == "01 02"
    assert cell_text(frame_record, "data", "dec") == "1 2"
    assert cell_text(frame_record, "data", "bin") == "00000001 00000010"
    assert cell_text(frame_record, "message", "text") == "VehicleStatus"
    assert cell_text(frame_record, "status", "status") == DECODE_DECODED
    assert cell_text(frame_record, "direction", "text") == "RX"
    assert cell_text(event_record, "status", "status") == "error_frame"
    assert cell_text(event_record, "data", "hex") == "ErrorFrame"
    assert cell_text(event_record, "id", "hex") == ""


def test_extended_identifiers_stay_visible_in_the_id_column():
    buffer = TraceBuffer()
    record = buffer.add_frame(CanFrame(0.0, 0x1ABCDEF, b"", is_extended_id=True))

    assert cell_text(record, "id", "hex") == "0x1ABCDEFx"
    assert matches(record, TraceFilterSettings(arbitration_id="1abcdef"))
    assert matches(record, TraceFilterSettings(arbitration_id="1abcdefx"))


def test_trace_uses_frame_direction_and_declared_remote_dlc():
    buffer = TraceBuffer()
    record = buffer.add_frame(
        CanFrame(0.0, 0x123, b"", is_remote_frame=True, direction="tx", declared_dlc=8)
    )

    assert cell_text(record, "direction", "text") == "TX"
    assert cell_text(record, "dlc", "dec") == "8"


# --------------------------------------------------------------------------
# item_113 - acquisition-wide, CAN-frame-only received sequence
# --------------------------------------------------------------------------


def test_received_frames_get_a_monotonic_session_sequence_and_events_stay_blank():
    buffer = _buffer()
    records = list(buffer)

    assert records[0].frame_number == 1
    assert records[1].frame_number == 2
    assert records[2].frame_number is None  # the BusEvent row
    assert cell_text(records[0], "frame", "text") == "1"
    assert cell_text(records[2], "frame", "text") == ""


def test_the_frame_sequence_survives_buffer_rotation_and_stays_global():
    buffer = TraceBuffer(capacity=3)
    for index in range(5):
        buffer.add_frame(CanFrame(float(index), 0x100 + index, b"\x00"))

    retained = [record.frame_number for record in buffer]
    assert retained == [3, 4, 5]


def test_a_new_session_restarts_the_frame_sequence_at_one():
    buffer = TraceBuffer(capacity=3)
    buffer.add_frame(CanFrame(0.0, 0x100, b"\x00"))
    buffer.add_frame(CanFrame(1.0, 0x101, b"\x00"))

    buffer.clear()
    record = buffer.add_frame(CanFrame(2.0, 0x102, b"\x00"))

    assert record.frame_number == 1


def test_the_frame_sequence_ignores_interleaved_events():
    buffer = TraceBuffer()
    buffer.add_event(BusEvent(0.0, "reconnecting", "driver restart"))
    first = buffer.add_frame(CanFrame(1.0, 0x100, b"\x00"))
    buffer.add_event(BusEvent(2.0, "error_frame", "bus error"))
    second = buffer.add_frame(CanFrame(3.0, 0x101, b"\x00"))

    assert (first.frame_number, second.frame_number) == (1, 2)


def test_default_trace_columns_show_the_frame_sequence_first():
    columns = default_trace_columns()

    assert columns[0].key == "frame"
    assert columns[0].visible is True


def test_the_frame_column_header_explains_that_retention_stays_bounded(qtbot):
    buffer = TraceBuffer(capacity=25)
    buffer.add_frame(CanFrame(0.0, 0x123, b"\x01"))
    panel = TraceViewPanel()
    qtbot.addWidget(panel)
    panel.set_buffer(buffer)
    panel.apply_columns(default_trace_columns())

    header_item = panel.table.horizontalHeaderItem(0)

    assert panel.table.horizontalHeaderItem(0).text()
    assert "25" in header_item.toolTip()
    assert panel.table.item(0, 0).text() == "1"


def test_the_frame_column_survives_filtering_and_selection(qtbot):
    buffer = _buffer()
    panel = TraceViewPanel()
    qtbot.addWidget(panel)
    panel.set_buffer(buffer)
    panel.apply_columns(default_trace_columns())
    panel.apply_settings(TraceFilterSettings(show_events=False))

    assert panel.table.rowCount() == 2
    assert [panel.table.item(row, 0).text() for row in range(2)] == ["1", "2"]
    assert panel.select_record(0)
    assert panel.selected_index() == 0


def test_trace_context_menu_is_record_aware_for_events(qtbot, monkeypatch):
    buffer = TraceBuffer()
    buffer.add_event(BusEvent(1.0, "reconnecting", "driver restart"))
    panel = TraceViewPanel()
    qtbot.addWidget(panel)
    panel.set_buffer(buffer)
    panel.apply_columns(default_trace_columns())
    panel.show()
    qtbot.waitExposed(panel)
    actions: list[list[str]] = []

    def capture_menu(menu, position):
        del position
        actions.append([action.text() for action in menu.actions()])

    monkeypatch.setattr(QMenu, "exec_", capture_menu)

    panel._context_menu(QPoint(1, max(1, panel.table.rowHeight(0) // 2)))

    assert actions == [["Copy row"]]
