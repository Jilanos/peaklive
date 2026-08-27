"""item_030 - a responsive, bounded acquisition lifecycle.

Every test here drives the shell through a *controllably* slow or failing
adapter. The point is never that the operation succeeds; it is that the window
keeps processing events while the operation is in flight, and that the shell
lands in a deterministic, usable state afterwards.
"""

from threading import Event

from PySide6.QtCore import QTimer

from peaklive.adapters import FakeCanAdapter
from peaklive.domain import BusEvent, MeasurementProfile
from peaklive.services.lifecycle import AcquisitionPhase
from peaklive.services.profiles import ProfileStore
from peaklive.ui import MainWindow
from peaklive.ui.session_controller import _ABANDONED_WORKERS


class ControlledAdapter(FakeCanAdapter):
    """A fake whose lifecycle calls can be held open or made to fail.

    Each gate starts open. Clearing one parks the worker thread inside that
    driver call for as long as the test wants, which is exactly the hardware
    condition the operator reported.
    """

    def __init__(
        self,
        connect_error: str | None = None,
        disconnect_error: str | None = None,
        receive_error: str | None = None,
    ) -> None:
        super().__init__()
        self.connect_gate = Event()
        self.connect_gate.set()
        self.disconnect_gate = Event()
        self.disconnect_gate.set()
        self.connect_error = connect_error
        self.disconnect_error = disconnect_error
        self.receive_error = receive_error
        self.disconnect_calls = 0

    def connect(self, profile: MeasurementProfile) -> BusEvent:
        self.connect_gate.wait(timeout=10.0)
        if self.connect_error is not None:
            raise RuntimeError(self.connect_error)
        return super().connect(profile)

    def receive(self, timeout: float):
        if self.receive_error is not None:
            raise RuntimeError(self.receive_error)
        return super().receive(timeout)

    def disconnect(self) -> BusEvent:
        self.disconnect_calls += 1
        self.disconnect_gate.wait(timeout=10.0)
        if self.disconnect_error is not None:
            raise RuntimeError(self.disconnect_error)
        return super().disconnect()


class EventLoopProbe:
    """Counts UI-thread timer ticks, so 'still responsive' is a measurement."""

    def __init__(self) -> None:
        self.ticks = 0
        self._timer = QTimer()
        self._timer.setInterval(5)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        self.ticks += 1

    def stop(self) -> None:
        self._timer.stop()

    def observe(self, qtbot, ticks: int = 3) -> None:
        """Fail unless the UI thread processes at least `ticks` more events."""
        target = self.ticks + ticks
        qtbot.waitUntil(lambda: self.ticks >= target, timeout=3_000)


def _window(qtbot, tmp_path, adapter: ControlledAdapter | None = None):
    adapter = adapter or ControlledAdapter()
    window = MainWindow(ProfileStore(tmp_path), adapter_factory=lambda: adapter)
    window.selected_profile.recording.enabled = False
    qtbot.addWidget(window)
    # A short bound keeps the timeout paths quick without changing their shape.
    window._shutdown_timeout_ms = 300
    return window, adapter


def _phase(window) -> AcquisitionPhase:
    return window._lifecycle.phase


# --------------------------------------------------------------------------
# AC1 - the window stays interactive under delayed lifecycle operations
# --------------------------------------------------------------------------


def test_a_blocking_connect_does_not_freeze_the_window(qtbot, tmp_path):
    window, adapter = _window(qtbot, tmp_path)
    adapter.connect_gate.clear()
    probe = EventLoopProbe()

    window._start_acquisition()

    assert _phase(window) is AcquisitionPhase.STARTING
    assert window.bus_state == "connecting"
    probe.observe(qtbot)

    adapter.connect_gate.set()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.RUNNING)
    probe.stop()

    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled())


def test_a_blocking_disconnect_does_not_freeze_the_window(qtbot, tmp_path):
    window, adapter = _window(qtbot, tmp_path)
    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.RUNNING)
    adapter.disconnect_gate.clear()
    probe = EventLoopProbe()

    window._stop_acquisition()

    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.FINALIZING)
    assert window.bus_state == "stopping"
    probe.observe(qtbot)

    adapter.disconnect_gate.set()
    qtbot.waitUntil(lambda: window.start_button.isEnabled(), timeout=5_000)
    probe.stop()
    assert _phase(window) is AcquisitionPhase.STOPPED
    assert window.bus_state == "stopped"


# --------------------------------------------------------------------------
# AC2 - one terminal result per generation, whatever the operator does
# --------------------------------------------------------------------------


def test_repeated_start_activation_opens_only_one_generation(qtbot, tmp_path):
    window, _ = _window(qtbot, tmp_path)

    window._start_acquisition()
    generation = window._lifecycle.generation
    worker = window._worker
    window._start_acquisition()
    window._start_acquisition()

    assert window._lifecycle.generation == generation
    assert window._worker is worker

    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled())


def test_repeated_stop_activation_is_harmless(qtbot, tmp_path):
    window, adapter = _window(qtbot, tmp_path)
    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.RUNNING)

    window._stop_acquisition()
    window._stop_acquisition()
    window._stop_acquisition()

    qtbot.waitUntil(lambda: window.start_button.isEnabled())
    assert adapter.disconnect_calls == 1
    assert _phase(window) is AcquisitionPhase.STOPPED


def test_a_stale_generation_cannot_restart_the_controls(qtbot, tmp_path):
    window, _ = _window(qtbot, tmp_path)
    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.RUNNING)
    stale = window._lifecycle.generation - 1

    # Exactly what an abandoned worker's queued signals look like on arrival.
    window._worker_phase_changed(stale, AcquisitionPhase.STOPPED)
    window._acquisition_finished(stale)

    assert _phase(window) is AcquisitionPhase.RUNNING
    assert window._worker is not None
    assert not window.start_button.isEnabled()

    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled())


# --------------------------------------------------------------------------
# AC3 - a bounded shutdown that degrades instead of hanging
# --------------------------------------------------------------------------


def test_a_shutdown_that_overruns_becomes_an_actionable_degraded_state(qtbot, tmp_path):
    window, adapter = _window(qtbot, tmp_path)
    window.show()
    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.RUNNING)
    adapter.disconnect_gate.clear()
    probe = EventLoopProbe()

    window._stop_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.TIMED_OUT, timeout=3_000)

    # Degraded, explained, and still interactive - never a silent freeze.
    assert window.bus_state == "degraded"
    assert window.session_note.isVisible()
    assert "close peaklive" in window.session_note.text().lower()
    assert window.session_note.level == "warning"
    assert not window.progress.isVisible()
    probe.observe(qtbot)

    # Reopening the channel is refused while the old worker may still hold it.
    assert not window.start_button.isEnabled()
    window._start_acquisition()
    assert _phase(window) is AcquisitionPhase.TIMED_OUT

    adapter.disconnect_gate.set()
    probe.stop()
    qtbot.waitUntil(lambda: window.start_button.isEnabled(), timeout=5_000)
    assert _phase(window) is AcquisitionPhase.STOPPED


def test_closing_during_a_blocked_shutdown_does_not_wait_unbounded(qtbot, tmp_path):
    window, adapter = _window(qtbot, tmp_path)
    window.show()
    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.RUNNING)
    adapter.disconnect_gate.clear()
    worker = window._worker

    # closeEvent waits at most the bounded interval, then abandons the worker.
    assert window.close()
    assert window._worker is None
    # Abandoned, but still referenced: destroying a running QThread aborts Qt.
    assert worker in _ABANDONED_WORKERS

    adapter.disconnect_gate.set()
    qtbot.waitUntil(lambda: worker not in _ABANDONED_WORKERS, timeout=5_000)


# --------------------------------------------------------------------------
# AC4 - every failure path lands in a deterministic usable state
# --------------------------------------------------------------------------


def test_a_connect_failure_restores_a_usable_state(qtbot, tmp_path):
    window, _ = _window(
        qtbot, tmp_path, ControlledAdapter(connect_error="adapter refused the bitrate")
    )

    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.FAILED)

    assert window.bus_state == "bus_error"
    assert window.start_button.isEnabled()
    assert not window.stop_button.isEnabled()
    assert not window.progress.isVisible()


def test_a_receive_failure_restores_a_usable_state(qtbot, tmp_path):
    window, adapter = _window(
        qtbot, tmp_path, ControlledAdapter(receive_error="driver read failed")
    )

    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.FAILED)

    # The driver was still closed on the way out, despite the receive error.
    assert adapter.disconnect_calls == 1
    assert window.start_button.isEnabled()
    assert not window.stop_button.isEnabled()


def test_a_disconnect_failure_restores_a_usable_state(qtbot, tmp_path):
    window, _ = _window(
        qtbot, tmp_path, ControlledAdapter(disconnect_error="driver handle already closed")
    )
    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.RUNNING)

    window._stop_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.FAILED)

    assert window.start_button.isEnabled()
    assert not window.stop_button.isEnabled()
    assert not window.progress.isVisible()


def test_a_failed_generation_can_be_started_again(qtbot, tmp_path):
    adapter = ControlledAdapter(connect_error="adapter refused the bitrate")
    window, _ = _window(qtbot, tmp_path, adapter)

    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.FAILED)

    adapter.connect_error = None
    window._start_acquisition()
    qtbot.waitUntil(lambda: _phase(window) is AcquisitionPhase.RUNNING)

    window._stop_acquisition()
    qtbot.waitUntil(lambda: window.start_button.isEnabled())
