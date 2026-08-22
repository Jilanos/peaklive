from peaklive.adapters import FakeCanAdapter
from peaklive.domain import MeasurementProfile
from peaklive.recording import AscRecorder
from peaklive.services import AcquisitionSession


def test_session_records_every_ingested_frame_before_any_ui_filter(tmp_path):
    profile = MeasurementProfile(name="Bench")
    profile.recording.directory = str(tmp_path)
    adapter = FakeCanAdapter()
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    session = AcquisitionSession(adapter, recorder)

    session.start(profile)
    frames = session.ingest(adapter.frames())
    session.stop()

    capture = next(tmp_path.glob("*.asc"))
    content = capture.read_text(encoding="utf-8")
    assert len(frames) == 32
    assert sum("Rx   d" in line for line in content.splitlines()) == 32
