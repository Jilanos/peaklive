from peaklive.adapters import FakeCanAdapter
from peaklive.domain import BusEvent, MeasurementProfile
from peaklive.services.worker import AcquisitionWorker


class EventAdapter(FakeCanAdapter):
    def __init__(self) -> None:
        super().__init__()
        self._event_pending = True

    def receive(self, timeout: float):
        if self._event_pending:
            self._event_pending = False
            return BusEvent(1.0, "error_frame", "PCAN error frame 0x4", "channel-1")
        return super().receive(timeout)


def test_worker_records_before_emitting_frames(qtbot, tmp_path):
    profile = MeasurementProfile(name="Worker")
    profile.recording.directory = str(tmp_path)
    worker = AcquisitionWorker(FakeCanAdapter(), profile)
    received: list = []
    worker.frames_received.connect(received.extend)

    worker.start()
    qtbot.waitUntil(lambda: len(received) == 32)
    worker.request_stop()
    qtbot.waitUntil(lambda: not worker.isRunning())

    capture = next(tmp_path.glob("*.asc"))
    assert len(received) == 32
    assert sum("Rx   d" in line for line in capture.read_text(encoding="utf-8").splitlines()) == 32


def test_worker_records_adapter_events_without_emitting_them_as_frames(qtbot, tmp_path):
    profile = MeasurementProfile(name="Worker events")
    profile.recording.directory = str(tmp_path)
    worker = AcquisitionWorker(EventAdapter(), profile)
    received_frames: list = []
    received_events: list = []
    worker.frames_received.connect(received_frames.extend)
    worker.event_received.connect(received_events.append)

    worker.start()
    qtbot.waitUntil(lambda: len(received_frames) == 32 and len(received_events) == 1)
    worker.request_stop()
    qtbot.waitUntil(lambda: not worker.isRunning())

    capture = next(tmp_path.glob("*.asc"))
    content = capture.read_text(encoding="utf-8")
    assert len(received_frames) == 32
    assert received_events[0].kind == "error_frame"
    assert "ErrorFrame" in content
    assert "PCAN error frame 0x4" in next(tmp_path.glob("*.jsonl")).read_text(encoding="utf-8")
