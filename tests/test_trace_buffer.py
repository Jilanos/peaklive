import pytest

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
