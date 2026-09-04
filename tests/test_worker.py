import pytest

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import BusEvent, MeasurementProfile
from peaklive.recording import AscRecorder
from peaklive.services import worker as worker_module
from peaklive.services.acquisition import AcquisitionSession
from peaklive.services.worker import (
    ERRORS_BEFORE_RECONNECT,
    MAX_RECONNECT_ATTEMPTS,
    AcquisitionWorker,
)


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
    # Pin the thresholds so the host's free disk space cannot change the result.
    profile.recording.warn_free_bytes = 1
    profile.recording.stop_free_bytes = 1
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
    profile.recording.warn_free_bytes = 1
    profile.recording.stop_free_bytes = 1
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


def test_worker_reports_a_successful_reservation_and_advances_the_iteration(qtbot, tmp_path):
    profile = MeasurementProfile(name="Reserved")
    profile.recording.directory = str(tmp_path)
    profile.recording.iteration = 1
    worker = AcquisitionWorker(FakeCanAdapter(), profile)
    reserved: list = []
    worker.recording_reserved.connect(reserved.append)

    worker.start()
    qtbot.waitUntil(lambda: bool(reserved))
    worker.request_stop()
    qtbot.waitUntil(lambda: not worker.isRunning())

    assert profile.recording.iteration == 2


def test_worker_never_reports_a_reservation_when_recording_is_disabled(qtbot, tmp_path):
    profile = MeasurementProfile(name="Monitor only")
    profile.recording.directory = str(tmp_path)
    profile.recording.enabled = False
    worker = AcquisitionWorker(FakeCanAdapter(), profile)
    received_frames: list = []
    reserved: list = []
    worker.frames_received.connect(received_frames.extend)
    worker.recording_reserved.connect(reserved.append)

    worker.start()
    qtbot.waitUntil(lambda: len(received_frames) == 32)
    worker.request_stop()
    qtbot.waitUntil(lambda: not worker.isRunning())

    assert not reserved
    assert not list(tmp_path.glob("*.asc"))


def test_worker_surfaces_a_recording_disk_warning_as_an_event(qtbot, tmp_path):
    profile = MeasurementProfile(name="Low disk")
    profile.recording.directory = str(tmp_path)
    # Warn on any free space, but never reach the stop threshold.
    profile.recording.warn_free_bytes = 2**60
    profile.recording.stop_free_bytes = 1
    worker = AcquisitionWorker(FakeCanAdapter(), profile)
    received_frames: list = []
    warnings: list = []
    worker.frames_received.connect(received_frames.extend)
    worker.event_received.connect(
        lambda event: warnings.append(event) if event.kind == "recording_warning" else None
    )

    worker.start()
    qtbot.waitUntil(lambda: len(received_frames) == 32 and bool(warnings))
    worker.request_stop()
    qtbot.waitUntil(lambda: not worker.isRunning())

    # Warned once, and the acquisition still delivered every frame.
    assert len(warnings) == 1
    assert "disk space is low" in warnings[0].message
    assert len(received_frames) == 32


class RefusingRecorder(AscRecorder):
    """Simulates a writer that cannot take ownership of a reserved target."""

    def start(self, settings, profile_name, now=None, reservation=None):
        raise RuntimeError("disk write refused")


def test_a_post_connect_start_failure_disconnects_the_adapter_exactly_once(
    qtbot, tmp_path, monkeypatch
):
    monkeypatch.setattr(worker_module, "AscRecorder", RefusingRecorder)
    disconnects: list = []
    adapter = FakeCanAdapter()
    original_disconnect = adapter.disconnect

    def counting_disconnect():
        disconnects.append(True)
        return original_disconnect()

    adapter.disconnect = counting_disconnect
    profile = MeasurementProfile(name="Refused")
    profile.recording.directory = str(tmp_path)
    worker = AcquisitionWorker(adapter, profile)
    failures: list = []
    worker.acquisition_failed.connect(failures.append)

    worker.start()
    qtbot.waitUntil(lambda: not worker.isRunning())

    assert failures and "disk write refused" in failures[0]
    assert disconnects == [True]
    assert not adapter.connected


def test_a_later_start_can_reconnect_after_a_post_connect_start_failure(
    qtbot, tmp_path, monkeypatch
):
    monkeypatch.setattr(worker_module, "AscRecorder", RefusingRecorder)
    adapter = FakeCanAdapter()
    failed_profile = MeasurementProfile(name="Refused")
    failed_profile.recording.directory = str(tmp_path)
    failed_worker = AcquisitionWorker(adapter, failed_profile)
    failed_worker.start()
    qtbot.waitUntil(lambda: not failed_worker.isRunning())
    assert not adapter.connected

    monkeypatch.setattr(worker_module, "AscRecorder", AscRecorder)
    retry_profile = MeasurementProfile(name="Retry")
    retry_profile.recording.enabled = False
    retry_worker = AcquisitionWorker(adapter, retry_profile)
    received_frames: list = []
    retry_worker.frames_received.connect(received_frames.extend)

    retry_worker.start()
    qtbot.waitUntil(lambda: len(received_frames) == 32)
    retry_worker.request_stop()
    qtbot.waitUntil(lambda: not retry_worker.isRunning())

    assert not adapter.connected


def _no_sleep(monkeypatch) -> None:
    """Error backoff and reconnect backoff are real msleep() calls; skip them."""
    monkeypatch.setattr(worker_module.AcquisitionWorker, "msleep", lambda self, ms: None)


def test_identical_error_events_are_rate_limited(tmp_path, monkeypatch):
    _no_sleep(monkeypatch)
    profile = MeasurementProfile(name="Noisy")
    profile.recording.directory = str(tmp_path)
    session = AcquisitionSession(FakeCanAdapter(), AscRecorder())
    session.start(profile)
    worker = AcquisitionWorker(FakeCanAdapter(), profile)
    received: list = []
    worker.event_received.connect(received.append)

    for _ in range(10):
        worker._handle_event(session, BusEvent(0.0, "error_frame", "PCAN driver error"))

    # Nine identical, back-to-back errors were dropped; only the first surfaced.
    assert len(received) == 1
    assert received[0].kind == "error_frame"


def test_error_backoff_grows_with_consecutive_errors_and_is_capped(tmp_path, monkeypatch):
    slept_ms: list[int] = []
    monkeypatch.setattr(
        worker_module.AcquisitionWorker, "msleep", lambda self, ms: slept_ms.append(ms)
    )
    profile = MeasurementProfile(name="Noisy")
    profile.recording.directory = str(tmp_path)
    profile.recording.enabled = False
    session = AcquisitionSession(FakeCanAdapter(), AscRecorder())
    session.start(profile)
    worker = AcquisitionWorker(FakeCanAdapter(), profile)

    for index in range(ERRORS_BEFORE_RECONNECT - 1):
        worker._handle_event(session, BusEvent(0.0, "error_frame", f"error {index}"))

    assert slept_ms == sorted(slept_ms)
    assert slept_ms[-1] == max(slept_ms)
    assert all(ms <= 1000 for ms in slept_ms)


def test_a_non_error_event_resets_the_error_streak(tmp_path, monkeypatch):
    _no_sleep(monkeypatch)
    profile = MeasurementProfile(name="Noisy")
    profile.recording.directory = str(tmp_path)
    profile.recording.enabled = False
    session = AcquisitionSession(FakeCanAdapter(), AscRecorder())
    session.start(profile)
    worker = AcquisitionWorker(FakeCanAdapter(), profile)

    for index in range(ERRORS_BEFORE_RECONNECT - 1):
        worker._handle_event(session, BusEvent(0.0, "error_frame", f"error {index}"))
    worker._handle_event(session, BusEvent(0.0, "connected", "back up"))

    assert worker._consecutive_errors == 0


def test_a_persistent_error_storm_triggers_a_bounded_alerted_reconnect(tmp_path, monkeypatch):
    _no_sleep(monkeypatch)
    profile = MeasurementProfile(name="Noisy")
    profile.recording.directory = str(tmp_path)
    profile.recording.enabled = False
    adapter = FakeCanAdapter()
    session = AcquisitionSession(adapter, AscRecorder())
    session.start(profile)
    worker = AcquisitionWorker(adapter, profile)
    received: list = []
    worker.event_received.connect(received.append)

    for index in range(ERRORS_BEFORE_RECONNECT):
        worker._handle_event(session, BusEvent(0.0, "error_frame", f"error {index}"))

    assert any(event.kind == "reconnecting" for event in received)
    assert any(event.kind == "connected" for event in received)
    assert worker._consecutive_errors == 0
    assert session.connected
    assert adapter.connected


class NeverReconnectsAdapter(FakeCanAdapter):
    def __init__(self) -> None:
        super().__init__()
        self._first_connect = True

    def connect(self, profile):
        if self._first_connect:
            self._first_connect = False
            return super().connect(profile)
        raise RuntimeError("still unreachable")


def test_exhausting_every_reconnect_attempt_raises_a_restartable_failure(tmp_path, monkeypatch):
    _no_sleep(monkeypatch)
    profile = MeasurementProfile(name="Gone")
    profile.recording.directory = str(tmp_path)
    profile.recording.enabled = False
    adapter = NeverReconnectsAdapter()
    session = AcquisitionSession(adapter, AscRecorder())
    session.start(profile)
    worker = AcquisitionWorker(adapter, profile)
    received: list = []
    worker.event_received.connect(received.append)

    with pytest.raises(RuntimeError, match="reconnect attempts"):
        for index in range(ERRORS_BEFORE_RECONNECT):
            worker._handle_event(session, BusEvent(0.0, "error_frame", f"error {index}"))

    reconnect_notices = [event for event in received if event.kind == "reconnecting"]
    assert len(reconnect_notices) == MAX_RECONNECT_ATTEMPTS
    assert not session.connected
