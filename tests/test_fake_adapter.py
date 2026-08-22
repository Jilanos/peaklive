from peaklive.adapters import FakeCanAdapter
from peaklive.domain import MeasurementProfile


def test_fake_adapter_emits_frames_only_when_connected():
    adapter = FakeCanAdapter()
    assert list(adapter.frames()) == []

    event = adapter.connect(MeasurementProfile(name="Test"))
    frames = list(adapter.frames())

    assert event.kind == "connected"
    assert adapter.connected is True
    assert len(frames) == 32
    assert frames[0].arbitration_id == 0x120

    assert adapter.disconnect().kind == "disconnected"
    assert adapter.connected is False
