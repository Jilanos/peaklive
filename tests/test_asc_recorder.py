from datetime import datetime

import pytest

from peaklive.domain import BusEvent, CanFrame, RecordingSettings
from peaklive.recording import EMPTY_TEXT_COMPONENT, AscRecorder, RecordingStopped


def _settings(tmp_path, **overrides):
    settings = RecordingSettings(directory=str(tmp_path), iteration=7)
    for name, value in overrides.items():
        setattr(settings, name, value)
    return settings


def test_recorder_writes_compatible_asc_and_event_sidecar(tmp_path):
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    started = recorder.start(_settings(tmp_path), "Vehicle test", datetime(2026, 8, 22, 9, 30))
    recorder.write_frame(CanFrame(10.0, 0x123, b"\x01\x02"))
    recorder.write_frame(CanFrame(10.1, 0x18FEF100, b"\xaa", is_extended_id=True))
    recorder.write_event(BusEvent(10.2, "error_frame", "bus warning"))
    recorder.write_event(BusEvent(10.3, "disconnected", "USB removed"))
    result = recorder.stop()

    assert result.incomplete is False
    assert result.segments == [started]
    content = started.read_text(encoding="utf-8")
    assert "Begin Triggerblock" in content
    assert "0.000000 1  123" in content
    assert "18FEF100x" in content
    assert "ErrorFrame" in content
    assert "PeakLive disconnected: USB removed" in content
    assert content.rstrip().endswith("End Triggerblock")
    assert started.with_suffix(".peaklive-events.jsonl").exists()


def test_recorder_writes_replayable_pcan_view_text_trc(tmp_path):
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    settings = _settings(tmp_path, capture_format="trc")
    started = recorder.start(settings, "Vehicle test", datetime(2026, 8, 22, 9, 30))
    recorder.write_frame(CanFrame(10.0, 0x123, b"\x01\x02", channel="channel-2"))
    recorder.write_frame(
        CanFrame(10.1, 0x18FEF100, b"", "channel-2", True, True)
    )
    recorder.stop()

    assert started.suffix == ".trc"
    content = started.read_text(encoding="utf-8")
    assert "2) 0.000 Rx 123 d 2 01 02" in content
    assert "2) 100.000 Rx 18FEF100x r 0" in content


def test_recorder_rotates_without_overwrite(tmp_path):
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    recorder.start(_settings(tmp_path, rotate_bytes=1), "Bench", datetime(2026, 8, 22, 9, 30))
    recorder.write_frame(CanFrame(1.0, 0x123, b"\x00"))
    recorder.write_frame(CanFrame(2.0, 0x123, b"\x01"))
    result = recorder.stop()

    assert len(result.segments) >= 2
    assert len({segment.name for segment in result.segments}) == len(result.segments)


def test_an_event_only_recording_still_rotates(tmp_path):
    """A stream of nothing but adapter events must not grow one segment forever."""
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    recorder.start(_settings(tmp_path, rotate_bytes=1), "Bench", datetime(2026, 8, 22, 9, 30))
    recorder.write_event(BusEvent(1.0, "error_frame", "bus warning"))
    recorder.write_event(BusEvent(2.0, "error_frame", "bus warning"))
    result = recorder.stop()

    assert len(result.segments) >= 2
    assert len({segment.name for segment in result.segments}) == len(result.segments)


def test_low_space_leaves_recoverable_partial_capture(tmp_path):
    recorder = AscRecorder(free_space=lambda path: 1)
    recorder.start(_settings(tmp_path, stop_free_bytes=2), "Bench", datetime(2026, 8, 22, 9, 30))

    with pytest.raises(RecordingStopped):
        recorder.write_frame(CanFrame(1.0, 0x123, b"\x00"))

    assert recorder.stop().incomplete is True
    assert list(tmp_path.glob("*.partial"))


def test_every_rotated_segment_and_sidecar_carries_the_operator_text(tmp_path):
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    recorder.start(
        _settings(tmp_path, rotate_bytes=1, text="roulage BL"),
        "Bench",
        datetime(2026, 8, 22, 9, 30),
    )
    recorder.write_frame(CanFrame(1.0, 0x123, b"\x00"))
    recorder.write_frame(CanFrame(2.0, 0x123, b"\x01"))
    result = recorder.stop()

    assert len(result.segments) >= 2
    for segment in result.segments:
        assert "roulage_BL" in segment.name
        assert segment.with_suffix(".peaklive-events.jsonl").exists()


def test_an_empty_text_still_produces_the_documented_stable_basename(tmp_path):
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    started = recorder.start(_settings(tmp_path), "Bench", datetime(2026, 8, 22, 9, 30))
    recorder.stop()

    assert EMPTY_TEXT_COMPONENT in started.name
    assert "__" not in started.name
