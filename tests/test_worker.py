from peaklive.adapters import FakeCanAdapter
from peaklive.domain import MeasurementProfile
from peaklive.services.worker import AcquisitionWorker


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
