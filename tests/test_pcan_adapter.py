from types import SimpleNamespace

import can
import pytest

from peaklive.adapters import PcanAdapter
from peaklive.domain import ControllerMode, MeasurementProfile


class StubBus:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.messages = [
            SimpleNamespace(
                timestamp=12.5,
                arbitration_id=0x18FEF100,
                data=bytearray(b"\x01\x02"),
                is_extended_id=True,
                is_remote_frame=False,
                is_error_frame=False,
            )
        ]
        self.closed = False

    def recv(self, timeout):
        return self.messages.pop(0) if self.messages else None

    def shutdown(self):
        self.closed = True


def test_pcan_adapter_maps_passive_profile_to_driver_state():
    stub = StubBus()

    def make_bus(**kwargs):
        stub.kwargs = kwargs
        return stub

    adapter = PcanAdapter(bus_factory=make_bus)
    profile = MeasurementProfile(name="Passive", controller_mode=ControllerMode.PASSIVE_LISTEN_ONLY)

    event = adapter.connect(profile)

    assert event.kind == "connected"
    assert stub.kwargs["interface"] == "pcan"
    assert stub.kwargs["state"] is can.BusState.PASSIVE
    assert stub.kwargs["receive_own_messages"] is False
    frame = next(adapter.frames())
    assert frame.arbitration_id == 0x18FEF100
    assert frame.is_extended_id is True
    assert adapter.disconnect().kind == "disconnected"
    assert stub.closed is True


def test_pcan_adapter_rejects_unconfigured_bitrates():
    adapter = PcanAdapter(bus_factory=lambda **kwargs: StubBus())
    profile = MeasurementProfile(name="Unsupported", bitrate=83_333)

    with pytest.raises(ValueError, match="Unsupported initial bitrate"):
        adapter.connect(profile)


def test_pcan_adapter_normalizes_driver_error_frames_to_events():
    bus = StubBus()
    bus.messages = [
        SimpleNamespace(
            timestamp=18.0,
            arbitration_id=0x4,
            data=bytearray(b"\x01\x08\x00\x00"),
            is_extended_id=False,
            is_remote_frame=False,
            is_error_frame=True,
        )
    ]
    adapter = PcanAdapter(bus_factory=lambda **kwargs: bus)
    adapter.connect(MeasurementProfile(name="Wrong bitrate"))

    event = adapter.receive(timeout=0)

    assert event.kind == "error_frame"
    assert event.message == "PCAN error frame 0x4 data=01 08 00 00"
    assert event.channel == "channel-1"


def test_pcan_adapter_frames_iterator_skips_driver_error_events():
    bus = StubBus()
    bus.messages = [
        SimpleNamespace(
            timestamp=18.0,
            arbitration_id=0x4,
            data=bytearray(b"\x01\x08\x00\x00"),
            is_extended_id=False,
            is_remote_frame=False,
            is_error_frame=True,
        ),
        SimpleNamespace(
            timestamp=19.0,
            arbitration_id=0x123,
            data=bytearray(b"\xAA"),
            is_extended_id=False,
            is_remote_frame=False,
            is_error_frame=False,
        ),
    ]
    adapter = PcanAdapter(bus_factory=lambda **kwargs: bus)
    adapter.connect(MeasurementProfile(name="Mixed"))

    frame = next(adapter.frames())

    assert frame.arbitration_id == 0x123


def test_pcan_adapter_normalizes_driver_overrun_exceptions():
    class OverrunBus(StubBus):
        def recv(self, timeout):
            raise can.CanOperationError("The receive queue was read too late")

    adapter = PcanAdapter(bus_factory=lambda **kwargs: OverrunBus())
    adapter.connect(MeasurementProfile(name="Overrun"))

    event = adapter.receive(timeout=0)

    assert event.kind == "driver_overrun"
    assert "receive queue was read too late" in event.message
