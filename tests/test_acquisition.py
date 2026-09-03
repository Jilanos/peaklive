import pytest

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


class FailingDisconnectAdapter(FakeCanAdapter):
    def disconnect(self):
        raise RuntimeError("driver handle already closed")


def test_a_disconnect_failure_still_finalizes_the_capture_as_recoverable(tmp_path):
    """A driver that fails on the way out must not also cost the capture."""
    profile = MeasurementProfile(name="Unclean")
    profile.recording.directory = str(tmp_path)
    adapter = FailingDisconnectAdapter()
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    session = AcquisitionSession(adapter, recorder)

    session.start(profile)
    session.ingest(adapter.frames())
    with pytest.raises(RuntimeError, match="driver handle already closed"):
        session.stop()

    # No clean .asc, but every frame is on disk as a recoverable .partial.
    assert not list(tmp_path.glob("*.asc"))
    partial = next(tmp_path.glob("*.asc.partial"))
    assert sum("Rx   d" in line for line in partial.read_text(encoding="utf-8").splitlines()) == 32
    assert not recorder.active


def test_an_unclean_stop_marks_the_capture_incomplete(tmp_path):
    profile = MeasurementProfile(name="Incomplete")
    profile.recording.directory = str(tmp_path)
    recorder = AscRecorder(free_space=lambda path: 20 * 1024**3)
    adapter = FakeCanAdapter()
    session = AcquisitionSession(adapter, recorder)

    session.start(profile)
    session.ingest(adapter.frames())
    session.stop(clean=False)

    assert not list(tmp_path.glob("*.asc"))
    assert next(tmp_path.glob("*.asc.partial")).exists()


def test_ingested_batches_are_flushed_so_a_blocked_shutdown_keeps_evidence(tmp_path):
    """The partial capture must be readable while the driver is still blocked."""
    profile = MeasurementProfile(name="Flushed")
    profile.recording.directory = str(tmp_path)
    adapter = FakeCanAdapter()
    session = AcquisitionSession(adapter, AscRecorder(free_space=lambda path: 20 * 1024**3))

    session.start(profile)
    session.ingest(adapter.frames())

    # Read the still-open partial: nothing is stranded in a Python buffer.
    partial = next(tmp_path.glob("*.asc.partial"))
    assert sum("Rx   d" in line for line in partial.read_text(encoding="utf-8").splitlines()) == 32


def test_a_successful_start_advances_the_persisted_iteration_by_one(tmp_path):
    profile = MeasurementProfile(name="Iterated")
    profile.recording.directory = str(tmp_path)
    profile.recording.iteration = 1
    session = AcquisitionSession(
        FakeCanAdapter(), AscRecorder(free_space=lambda path: 20 * 1024**3)
    )

    session.start(profile)
    session.stop()

    assert profile.recording.iteration == 2
    assert not list(tmp_path.glob("*.reserved"))


def test_start_skips_existing_evidence_and_uses_the_first_free_iteration(tmp_path):
    profile = MeasurementProfile(name="Guarded")
    profile.recording.directory = str(tmp_path)
    profile.recording.iteration = 1
    profile.recording.filename_template = "{profile}_{iteration:03d}"
    (tmp_path / "Guarded_001.asc").write_text("prior evidence", encoding="utf-8")
    (tmp_path / "Guarded_002.asc.partial").write_text("in progress", encoding="utf-8")
    session = AcquisitionSession(
        FakeCanAdapter(), AscRecorder(free_space=lambda path: 20 * 1024**3)
    )

    started = session.start(profile)
    session.stop()

    capture = next(tmp_path.glob("Guarded_003.asc"))
    assert capture.exists()
    assert (tmp_path / "Guarded_001.asc").read_text(encoding="utf-8") == "prior evidence"
    assert (tmp_path / "Guarded_002.asc.partial").read_text(encoding="utf-8") == "in progress"
    assert profile.recording.iteration == 4
    assert started.message


class RefusingRecorder(AscRecorder):
    """Simulates a writer that cannot take ownership of a reserved target."""

    def start(self, settings, profile_name, now=None, reservation=None):
        raise RuntimeError("disk write refused")


def test_a_failed_writer_start_releases_the_reservation_without_advancing_iteration(tmp_path):
    profile = MeasurementProfile(name="Refused")
    profile.recording.directory = str(tmp_path)
    profile.recording.iteration = 1
    session = AcquisitionSession(FakeCanAdapter(), RefusingRecorder())

    with pytest.raises(RuntimeError, match="disk write refused"):
        session.start(profile)

    assert profile.recording.iteration == 1
    assert not list(tmp_path.glob("*.reserved"))
