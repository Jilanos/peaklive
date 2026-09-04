"""item_064 coverage: live and replay stay mutually exclusive and isolated.

Starting the other source while one is active must be refused with a visible
alert and a disabled action, a running acquisition worker must never read the
profile the UI thread can still edit, and an invalid recording template must
never reach disk.
"""

from __future__ import annotations

from peaklive.adapters import FakeCanAdapter
from peaklive.recording import InvalidTemplateError
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow


class _RunningStub:
    """A stand-in worker that reports as running without any real thread.

    Only used to exercise the mutual-exclusion guards in isolation; the test
    clears it before teardown so the window's real close path never has to
    treat it as an actual QThread.
    """

    def isRunning(self) -> bool:  # noqa: N802 - matches QThread's own casing
        return True


def _window(qtbot, tmp_path) -> MainWindow:
    window = MainWindow(ProfileStore(tmp_path / "settings"), adapter_factory=FakeCanAdapter)
    window.selected_profile.recording.enabled = False
    qtbot.addWidget(window)
    return window


def test_starting_acquisition_is_refused_while_a_replay_is_running(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._replay_worker = _RunningStub()

    window._start_acquisition()

    assert window._worker is None
    assert window.session_note.level == "warning"
    assert "replay" in window.session_note.text().lower()
    window._replay_worker = None


def test_opening_a_trace_is_refused_while_acquisition_is_running(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._worker = _RunningStub()

    window._open_trace(tmp_path / "capture.asc")

    assert window._replay_worker is None
    assert window.session_note.level == "warning"
    assert "acquisition" in window.session_note.text().lower()
    window._worker = None


def test_start_action_is_disabled_while_a_replay_is_running(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._replay_worker = _RunningStub()

    window._update_mode_availability()

    assert not window.start_action.isEnabled()
    assert window.open_trace_action.isEnabled()
    window._replay_worker = None


def test_open_trace_action_is_disabled_while_acquisition_is_running(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window._worker = _RunningStub()

    window._update_mode_availability()

    assert not window.open_trace_action.isEnabled()
    assert window.start_action.isEnabled()
    window._worker = None


def test_both_actions_are_enabled_once_no_session_is_running(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._update_mode_availability()

    assert window.start_action.isEnabled()
    assert window.open_trace_action.isEnabled()


def test_a_running_acquisition_worker_never_shares_the_profile_object(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window._start_acquisition()
    qtbot.waitUntil(lambda: window._worker is not None)
    worker_profile = window._worker._profile

    assert worker_profile is not window.selected_profile
    assert worker_profile.name == window.selected_profile.name

    # A mid-session edit on the UI thread must never reach the worker's copy.
    window.selected_profile.recording.filename_template = "{profile}_edited"
    assert worker_profile.recording.filename_template != "{profile}_edited"

    window._stop_acquisition()
    qtbot.waitUntil(lambda: window._worker is None, timeout=5_000)


def test_a_completed_reservation_advances_the_shared_profiles_iteration(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    window.selected_profile.recording.enabled = True
    window.selected_profile.recording.directory = str(tmp_path)
    window.selected_profile.recording.iteration = 1

    window._start_acquisition()
    qtbot.waitUntil(lambda: window.selected_profile.recording.iteration == 2, timeout=5_000)

    stored = window._store.load()
    assert stored.selected.recording.iteration == 2


def test_recording_changed_never_persists_an_invalid_template(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)
    saves: list = []
    window._save = lambda: saves.append(True)  # type: ignore[method-assign]

    window.selected_profile.recording.filename_template = "{unsupported}"
    window._recording_changed()
    assert saves == []

    window.selected_profile.recording.filename_template = "{profile}_{iteration:03d}"
    window._recording_changed()
    assert saves == [True]


def test_an_invalid_template_never_reaches_the_persisted_store(qtbot, tmp_path):
    window = _window(qtbot, tmp_path)

    window.selected_profile.recording.filename_template = "{unsupported}"
    window._recording_changed()

    stored = window._store.load()
    from peaklive.recording import RecordingNaming

    naming = RecordingNaming()
    try:
        naming.validate_template(stored.selected.recording.filename_template)
    except InvalidTemplateError:
        raise AssertionError("an invalid template reached the persisted store") from None
